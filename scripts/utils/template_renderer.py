"""
Jinja2 Template Renderer for Open Travel Guide
Renders HTML pages from site-data JSON using Jinja2 templates.

Templates:
- region-template.html (rg- prefix classes) -> Region/Country hub pages
- topic-page-template.html (tp- prefix classes) -> Topic detail pages

Each template has its own separate stylesheet with unique class prefixes
to prevent any CSS conflicts.
"""

import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Dict, Any, List, Optional
from jinja2 import Environment, FileSystemLoader, select_autoescape

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


@lru_cache(maxsize=1)
def _load_site_config() -> Dict[str, Any]:
    """Read data/site_config.json once and cache. Holds non-secret site-wide
    config: GSC + Bing verification tokens, IndexNow key, feature flags.
    Missing file is non-fatal so old call sites that don't pass site_config
    still render."""
    cfg_path = Path(__file__).resolve().parent.parent.parent / "data" / "site_config.json"
    try:
        with open(cfg_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _compute_css_version() -> str:
    """sha1[:10] of base.css + theme.css contents. Stamped into the
    <link rel=stylesheet> URLs as ?v=<hash> so a CSS edit immediately
    invalidates every browser's cache without affecting unrelated
    resources. Pair with Cache-Control: immutable, max-age=1y on /css/*
    so the cached entry is sticky until the next render."""
    import hashlib
    css_dir = Path(__file__).resolve().parent.parent.parent / "content" / "css"
    hasher = hashlib.sha1()
    for name in ("base.css", "theme.css"):
        p = css_dir / name
        if p.exists():
            hasher.update(p.read_bytes())
    return hasher.hexdigest()[:10]


# 24 wine topics. shared across renderer, generator and templates.
WINE_TOPIC_NAV = [
    {'slug': 'vineyards',        'name': 'Vineyards',        'icon': '🍇'},
    {'slug': 'wines',            'name': 'Wines',            'icon': '🍷'},
    {'slug': 'tasting-rooms',    'name': 'Tasting Rooms',    'icon': '🍷'},
    {'slug': 'wine-bars',        'name': 'Wine Bars',        'icon': '🥂'},
    {'slug': 'wine-restaurants', 'name': 'Wine Restaurants', 'icon': '🍽️'},
    {'slug': 'wine-retailers',   'name': 'Wine Retailers',   'icon': '🛒'},
    {'slug': 'wine-schools',     'name': 'Wine Schools',     'icon': '🎓'},
    {'slug': 'wine-tours',       'name': 'Wine Tours',       'icon': '🚐'},
    {'slug': 'wine-festivals',   'name': 'Wine Festivals',   'icon': '🎉'},
    {'slug': 'distilleries',     'name': 'Distilleries',     'icon': '🥃'},
    {'slug': 'wine-museums',     'name': 'Wine Museums',     'icon': '🏛️'},
    {'slug': 'wine-hotels',      'name': 'Wine Hotels',      'icon': '🛏️'},
    {'slug': 'wine-experiences', 'name': 'Experiences',      'icon': '✨'},
    {'slug': 'signature-wines',  'name': 'Signature Wines',  'icon': '🍾'},
    {'slug': 'signature-grapes', 'name': 'Signature Grapes', 'icon': '🌿'},
    {'slug': 'budget-wines',     'name': 'Budget Wines',     'icon': '💶'},
    {'slug': 'hidden-gems',      'name': 'Hidden Gems',      'icon': '💎'},
    {'slug': 'day-trips-wine',   'name': 'Day Trips',        'icon': '🚆'},
    {'slug': 'itineraries',      'name': 'Itineraries',      'icon': '🗺️'},
    {'slug': 'wine-history',     'name': 'Wine History',     'icon': '📜'},
    {'slug': 'seasonal-wine',    'name': 'Seasonal',         'icon': '🍂'},
    {'slug': 'neighborhoods',    'name': 'Sub-Appellations', 'icon': '📍'},
    {'slug': 'nightlife',        'name': 'Nightlife',        'icon': '🌃'},
    {'slug': 'dietary',          'name': 'Biodynamic',       'icon': '🌱'},
    {'slug': 'food-pairing',     'name': 'Food Pairing',     'icon': '🧀'},
]

# Back-compat alias for any external import expecting the old name.
FOOD_TOPIC_NAV = WINE_TOPIC_NAV


class TemplateRenderer:
    """Render HTML pages using Jinja2 templates."""

    # Template mapping by page type
    TEMPLATE_MAP = {
        'REGION': 'region-template.html',
        'TOPIC': 'topics/_topic_base.html',  # generic fallback
        'HOME':   'home.html',
    }

    # Topic-specific templates. Only topics whose layout differs from the
    # generic card grid get an explicit template; the rest fall back to
    # topics/_topic_base.html, which renders a place_card grid over the
    # single topic list loaded for the page.
    TOPIC_TEMPLATE_MAP = {
        'vineyards':        'topics/vineyards-topic.html',
        'wines':            'topics/wines-topic.html',
        'wine-bars':        'topics/wine-bars-topic.html',
        'wine-restaurants': 'topics/wine-restaurants-topic.html',
        'wine-schools':     'topics/wine-schools-topic.html',
        'wine-tours':       'topics/wine-tours-topic.html',
        'wine-festivals':   'topics/wine-festivals-topic.html',
        'signature-wines':  'topics/signature-wines-topic.html',
        'signature-grapes': 'topics/signature-grapes-topic.html',
        'wine-history':     'topics/wine-history-topic.html',
        'seasonal-wine':    'topics/seasonal-wine-topic.html',
        'itineraries':      'topics/itineraries-topic.html',
        'dietary':          'topics/dietary-topic.html',
        'nightlife':        'topics/nightlife-topic.html',
        'food-pairing':     'topics/food-pairing-topic.html',
    }

    def __init__(self, templates_dir: str = None):
        """
        Initialize renderer with templates directory.

        Args:
            templates_dir: Path to templates directory.
                          Defaults to 'templates/' relative to repo root.
        """
        if templates_dir is None:
            # Default to repo root's templates directory
            repo_root = Path(__file__).parent.parent.parent
            templates_dir = repo_root / 'templates'

        self.templates_dir = Path(templates_dir)

        if not self.templates_dir.exists():
            raise FileNotFoundError(f"Templates directory not found: {self.templates_dir}")

        # Set up Jinja2 environment
        self.env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            autoescape=select_autoescape(['html', 'xml']),
            trim_blocks=True,
            lstrip_blocks=True,
        )

        # Expose site_config as a Jinja global so EVERY template can read
        # site-wide config (GSC verification, IndexNow key, feature flags)
        # without each generator having to thread it through context.
        self.env.globals['site_config'] = _load_site_config()
        # css_version: short content-hash stamped onto /css/* URLs as ?v=
        # so cache-busts happen the instant CSS changes (paired with
        # Cache-Control: immutable on /css/* in Caddy).
        self.env.globals['css_version'] = _compute_css_version()

        # Add custom filters
        self.env.filters['slugify'] = self._slugify
        self.env.filters['striptags'] = self._striptags
        # truncate_words is still registered for compatibility but must not be used
        # on card descriptions. it bakes '...' into the HTML. See
        # docs/specs/elipsis-fix/00-OVERVIEW.md.
        self.env.filters['truncate_words'] = self._truncate_words
        self.env.filters['safe_list'] = self._safe_list
        self.env.filters['format_price_range'] = self._format_price_range
        self.env.filters['humanize_duration'] = self._humanize_duration
        self.env.filters['price_to_int'] = self._price_to_int

    def render(self, data: Dict[str, Any], page_type: str = 'REGION', topic_slug: str = None) -> str:
        """
        Render a page from site-data.

        Args:
            data: Site-data dictionary
            page_type: 'REGION' or 'TOPIC'
            topic_slug: For TOPIC pages, the specific topic (e.g., 'attractions', 'hotels')
                       to use topic-specific templates

        Returns:
            Rendered HTML string
        """
        # Determine template name
        if page_type == 'TOPIC' and topic_slug:
            # Use topic-specific template if available
            template_name = self.TOPIC_TEMPLATE_MAP.get(topic_slug)
            if not template_name:
                # Fall back to generic topic template
                template_name = self.TEMPLATE_MAP.get('TOPIC')
        else:
            template_name = self.TEMPLATE_MAP.get(page_type)

        if not template_name:
            raise ValueError(f"Unknown page type: {page_type}. Valid types: {list(self.TEMPLATE_MAP.keys())}")

        template = self.env.get_template(template_name)

        # Prepare context with defaults
        context = self._prepare_context(data, page_type)

        return template.render(**context)

    def _prepare_context(self, data: Dict[str, Any], page_type: str) -> Dict[str, Any]:
        """Prepare template context with defaults for missing fields."""
        context = dict(data)  # Copy to avoid modifying original

        # Sanitize slugs. strip trailing slashes to prevent // in URLs
        for key in ('country_slug', 'region_slug'):
            if context.get(key):
                context[key] = context[key].strip('/')

        # Defensive normalization for sub-regions with schema drift.
        # Each block is independent; absence of one key never affects another.

        # 1) products: must be list of dicts. Some sub-regions stored a list of
        # type-slug strings (e.g. ['itinerary_7day', 'food_guide']) instead of
        # full product dicts. Filter out non-dict entries so the template's
        # `{% for product in products %}` loop never sees a string.
        if isinstance(context.get('products'), list):
            context['products'] = [p for p in context['products'] if isinstance(p, dict)]
        else:
            context['products'] = []

        # 2) research.best_time_to_visit: template expects a dict with .best /
        # .avoid keys. Some sub-regions store it as a bare string or None.
        # Normalize to a dict in either case.
        research = context.setdefault('research', {})
        btv = research.get('best_time_to_visit')
        if not isinstance(btv, dict):
            if isinstance(btv, str) and btv.strip():
                research['best_time_to_visit'] = {'best': btv, 'avoid': ''}
            else:
                research['best_time_to_visit'] = {'best': 'Year-round', 'avoid': 'None'}

        # 3) research.budget_breakdown: template expects .budget / .mid_range /
        # .luxury keys. Some sub-regions use 'budget_per_day' (+ '_per_day'
        # and '_per_day_usd' variants) or 'backpacker' in place of 'budget'.
        # Also: each canonical entry is read with .daily; if the variant has
        # only a string (e.g. "60-80"), wrap it in a dict that exposes .daily.
        bb = research.get('budget_breakdown')
        if isinstance(bb, dict):
            aliases = (('budget', ('budget_per_day', 'budget_per_day_usd', 'backpacker')),
                       ('mid_range', ('mid_range_per_day', 'mid_range_per_day_usd')),
                       ('luxury', ('luxury_per_day', 'luxury_per_day_usd')))
            for canonical, variants in aliases:
                if canonical not in bb:
                    for variant in variants:
                        if variant in bb:
                            v = bb[variant]
                            # If the variant value is a bare string ("60-80"),
                            # wrap so .daily access works in template.
                            bb[canonical] = v if isinstance(v, dict) else {'daily': v}
                            break

        # 4) research lists that the template slices with [:N]. Some sub-regions
        # store these as a dict-of-lists (e.g. hotels = {luxury:[], mid_range:[],
        # budget:[]}). Flatten dict values into a single list so [:N] works.
        for list_field in ('hotels', 'restaurants', 'top_attractions',
                           'hidden_gems', 'safety_tips', 'attractions'):
            val = research.get(list_field)
            if isinstance(val, dict):
                flat = []
                for v in val.values():
                    if isinstance(v, list):
                        flat.extend(v)
                research[list_field] = flat

        # 5) seo.pages: _prepare_seo (below) expects a dict keyed by topic slug.
        # Some sub-regions store it as a list (probably of page-spec dicts).
        # Coerce to empty dict; _prepare_seo will then use its own defaults.
        seo = context.get('seo')
        if isinstance(seo, dict) and not isinstance(seo.get('pages'), dict):
            seo['pages'] = {}

        # Compute base_path for relative asset references (logo, CSS, etc.)
        # Depth depends on page type and whether this is a subregion.
        has_region = bool(context.get('region_slug'))
        if page_type == 'REGION':
            context['base_path'] = '../..' if has_region else '..'
        elif page_type == 'TOPIC':
            context['base_path'] = '../../..' if has_region else '../..'
        else:
            context['base_path'] = '..'

        # ─── GA4 analytics context ──────────────────────────────────────────
        # These keys mirror what scripts/ga4_retrofit/inject.py produces for
        # the retrofitted pages so a regenerated page is byte-equivalent on
        # GA4-relevant lines. See docs/specs/ga4/02-template-and-generator-fixer.md.
        country_slug = context.get('country_slug')
        region_slug = context.get('region_slug')
        topic_slug = (context.get('topic') or {}).get('slug')
        if topic_slug == 'index':
            topic_slug = None

        if page_type == 'REGION':
            ga_page_type = 'subregion_index' if region_slug else 'country_index'
        elif page_type == 'TOPIC':
            ga_page_type = 'subregion_topic' if region_slug else 'country_topic'
        else:
            ga_page_type = 'unknown'

        ga_destination = region_slug or country_slug or 'global'

        ga_context_parts = []
        if country_slug:
            ga_context_parts.append(country_slug)
        if region_slug:
            ga_context_parts.append(region_slug)
        if topic_slug:
            ga_context_parts.append(topic_slug)
        ga_context = ':'.join(ga_context_parts) if ga_context_parts else ga_page_type

        context['analytics'] = {
            'measurement_id': '',  # TableJourney: GA not wired yet
            'page_type':      ga_page_type,
            'destination':    ga_destination,
            'country':        country_slug,
            'region':         region_slug,
            'context':        ga_context,
        }

        # Ensure destination has all required fields
        if 'destination' not in context:
            context['destination'] = {}
        dest_defaults = {
            'name': 'Unknown',
            'country': 'Unknown',
            'description': '',
            'overview': '',
        }
        for key, default in dest_defaults.items():
            if key not in context['destination']:
                context['destination'][key] = default

        # Expose hero_image_url at the top level so base.html can emit a
        # <link rel="preload" as="image"> for the LCP element. Match the
        # template's own fallback chain: destination.hero_image, then
        # research.hero_image. Prefer the 1200w variant since that's what
        # most desktop viewports end up requesting via srcset.
        if 'hero_image_url' not in context:
            _hero_src = (context.get('destination', {}).get('hero_image')
                         or context.get('research', {}).get('hero_image'))
            if _hero_src:
                _preload = (_hero_src
                            .replace('w=1600', 'w=1200')
                            .replace('h=900', 'h=675'))
                context['hero_image_url'] = _preload

        # Date helpers used as fallbacks in Event-type JSON-LD: schema.org
        # requires startDate on every Festival / EducationEvent subtype,
        # and Offer wants validFrom. Today / today+365 are stable defaults
        # for ongoing offerings without scheduled dates.
        import datetime as _dt_local
        _today = _dt_local.date.today()
        if 'current_date_iso' not in context:
            context['current_date_iso'] = _today.isoformat()
        if 'next_year_iso' not in context:
            context['next_year_iso'] = (_today + _dt_local.timedelta(days=365)).isoformat()

        # Ensure hub_page has all required fields
        if 'hub_page' not in context:
            context['hub_page'] = {}
        hub_defaults = {
            'title': f"{context['destination']['name']} Travel Guide 2025",
            'meta_description': f"Complete travel guide for {context['destination']['name']}",
            'url': f"/{context.get('country_slug', 'unknown')}/",
        }
        for key, default in hub_defaults.items():
            if key not in context['hub_page']:
                context['hub_page'][key] = default

        # Ensure research section exists
        if 'research' not in context:
            context['research'] = {}
        research_defaults = {
            'top_attractions': [],
            'hotels': [],
            'restaurants': [],
            'budget_breakdown': {
                'currency': 'USD',
                'budget': {'daily': '$50-100'},
                'mid_range': {'daily': '$100-200'},
                'luxury': {'daily': '$300+'},
            },
            'best_time_to_visit': {'best': 'Year-round', 'avoid': 'None'},
            'safety_tips': [],
            'hidden_gems': [],
            'transportation': {},
        }
        for key, default in research_defaults.items():
            if key not in context['research']:
                context['research'][key] = default

        # Ensure breadcrumb exists. page-type-aware, subregion-aware
        if 'breadcrumb' not in context:
            dest = context.get('destination', {})
            country_slug = context.get('country_slug', 'unknown')
            region_slug = context.get('region_slug')
            topic = context.get('topic', {})

            has_region = bool(region_slug)

            if has_region:
                country_name = dest.get('country', dest.get('name', ''))
                region_name = dest.get('name', '')
                state_name = dest.get('state')
                state_slug = dest.get('state_slug')

                crumbs = [
                    {'name': 'Home', 'url': '/'},
                    {'name': country_name, 'url': f'/{country_slug}/'},
                ]
                if state_name and state_slug:
                    crumbs.append({'name': state_name, 'url': f'/{country_slug}/{state_slug}/'})

                if topic.get('slug') and topic.get('slug') != 'index':
                    crumbs.append({'name': region_name, 'url': f'/{country_slug}/{region_slug}/'})
                    crumbs.append({'name': topic.get('name', ''), 'url': None})
                else:
                    crumbs.append({'name': region_name, 'url': None})
                context['breadcrumb'] = crumbs
            else:
                country_name = dest.get('name', '')

                if topic.get('slug') and topic.get('slug') != 'index':
                    context['breadcrumb'] = [
                        {'name': 'Home', 'url': '/'},
                        {'name': country_name, 'url': f'/{country_slug}/'},
                        {'name': topic.get('name', ''), 'url': None},
                    ]
                else:
                    context['breadcrumb'] = [
                        {'name': 'Home', 'url': '/'},
                        {'name': country_name, 'url': None},
                    ]

        # Ensure itineraries exist
        if 'itineraries' not in context:
            context['itineraries'] = self._generate_default_itineraries(context)

        # Ensure FAQs exist
        if 'faqs' not in context:
            context['faqs'] = self._generate_default_faqs(context)

        # Build full SEO structure from site-data seo schema
        context = self._prepare_seo(context)

        # Page type specific defaults
        if page_type == 'REGION':
            context = self._add_region_defaults(context)
        elif page_type == 'TOPIC':
            context = self._add_topic_defaults(context)

        return context

    def _prepare_seo(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Build full SEO structure for templates from site-data seo schema."""
        site_seo = context.get('seo', {})
        topic_obj = context.get('topic', {}) or {}
        topic_slug = topic_obj.get('slug', 'index')
        country_slug = context.get('country_slug', 'unknown')
        region_slug = context.get('region_slug')
        dest_name = context.get('destination', {}).get('name', 'Unknown')

        pages_seo = site_seo.get('pages', {})
        # Topic pages: use topic-specific title/desc if data didn't override per-page SEO.
        if topic_slug and topic_slug != 'index':
            topic_page_default = {
                'title': f"{topic_obj.get('h1') or topic_obj.get('name') or topic_slug} | Cork & Curve",
                'description': topic_obj.get('meta_description') or topic_obj.get('subtitle') or '',
            }
            page_seo = pages_seo.get(topic_slug, topic_page_default)
        else:
            page_seo = pages_seo.get('index', {})
        shared = site_seo.get('shared', {})
        geo = site_seo.get('geo', {})
        base_url = site_seo.get('base_url') or (_load_site_config().get('base_url')) or 'https://corkandcurve.com'

        # URL path: /<country>/[<region>/][<topic>/]
        path_parts = [country_slug]
        if region_slug:
            path_parts.append(region_slug)
        if topic_slug and topic_slug != 'index':
            path_parts.append(topic_slug)
        canonical_url = f"{base_url}/" + "/".join(path_parts) + "/"

        # OG image fallback chain — drives the link-preview thumbnail on
        # iMessage / Slack / WhatsApp / Twitter / Facebook. Order of
        # preference (revised 2026-05-19):
        #   1. /og/<city-slug>.jpg — branded city card (hero photo +
        #      gradient + "City" text + TableJourney wordmark). Built by
        #      scripts/build_og_cities.py. Wins because it carries our
        #      brand AND the city photo, whereas raw hero_image is just
        #      a stock Unsplash URL with no branding.
        #   2. destination.hero_image — raw food photo, used only when
        #      the branded card hasn't been built yet for this city.
        #   3. shared.og_image — explicit per-data override.
        #   4. /og/default.jpg — generic site card.
        city_slug = region_slug if region_slug else country_slug
        branded_og = REPO_ROOT / 'content' / 'og' / f'{city_slug}.jpg'
        if branded_og.exists():
            chosen_og = f'{base_url}/og/{city_slug}.jpg'
        else:
            hero_src = (context.get('destination', {}).get('hero_image')
                        or context.get('research', {}).get('hero_image'))
            if hero_src:
                chosen_og = (hero_src
                             .replace('w=1600', 'w=1200')
                             .replace('h=900',  'h=630')
                             .replace('h=1067', 'h=630'))
            else:
                chosen_og = shared.get('og_image',
                                       f'{base_url}/og/default.jpg')

        full_seo = {
            'meta': {
                'title': page_seo.get('title', f'{dest_name} Wine Guide | Cork & Curve'),
                'description': page_seo.get('description', f'Where to drink in {dest_name}: vineyards, tasting rooms, signature wines and wine culture, told by Cork & Curve editors.'),
                'canonical_url': canonical_url,
                'robots': shared.get('robots', 'index, follow, max-image-preview:large'),
                'author': 'Cork & Curve Editorial',
            },
            'open_graph': {
                'og_title': page_seo.get('title', f'{dest_name} Wine Guide'),
                'og_description': page_seo.get('description', f'Where to drink wine in {dest_name}.'),
                'og_image': chosen_og,
                'og_image_width': '1200', 'og_image_height': '630',
                'og_image_alt': shared.get('og_image_alt', f'{dest_name} wine guide'),
                'og_url': canonical_url, 'og_type': 'article',
                'og_site_name': 'Cork & Curve', 'og_locale': 'en_US',
            },
            'twitter': {
                'twitter_card': 'summary_large_image',
                'twitter_title': page_seo.get('title', f'{dest_name} Wine Guide'),
                'twitter_description': page_seo.get('description', f'Where to drink wine in {dest_name}.'),
                'twitter_image': shared.get('twitter_image', chosen_og),
                'twitter_image_alt': shared.get('og_image_alt', f'{dest_name} wine guide'),
            },
            'article': {
                'published_time': '2026-01-01T00:00:00Z',
                'modified_time': '2026-05-17T00:00:00Z',
                'author': 'Cork & Curve Editorial', 'section': 'Wine Travel',
            },
            'geo': {
                'place_name': geo.get('place_name', dest_name),
                'latitude': geo.get('latitude', '0.0'),
                'longitude': geo.get('longitude', '0.0'),
                'country_code': geo.get('country_code', 'XX'),
            },
            'structured_data': {'breadcrumb_items': self._build_breadcrumb_items(context, base_url)},
        }
        context['seo'] = full_seo
        return context

    def _build_breadcrumb_items(self, context: Dict[str, Any], base_url: str = 'https://corkandcurve.com') -> List[Dict]:
        """Build breadcrumb items for structured data."""
        country_slug = context.get('country_slug', 'unknown')
        region_slug = context.get('region_slug')
        dest = context.get('destination', {})
        topic = context.get('topic', {})

        items = [
            {'position': 1, 'name': 'Home', 'url': base_url},
        ]

        if region_slug:
            country_name = dest.get('country', dest.get('name', 'Unknown'))
            region_name = dest.get('name', 'Unknown')
            state_name = dest.get('state')
            state_slug = dest.get('state_slug')
            pos = 2
            items.append({'position': pos, 'name': country_name, 'url': f"{base_url}/{country_slug}/"})
            pos += 1
            if state_name and state_slug:
                items.append({'position': pos, 'name': state_name, 'url': f"{base_url}/{country_slug}/{state_slug}/"})
                pos += 1
            items.append({'position': pos, 'name': region_name, 'url': f"{base_url}/{country_slug}/{region_slug}/"})
            pos += 1
            if topic.get('slug') and topic.get('slug') != 'index':
                items.append({'position': pos, 'name': topic.get('name', ''), 'url': None})
        else:
            dest_name = dest.get('name', 'Unknown')
            items.append({'position': 2, 'name': dest_name, 'url': f"{base_url}/{country_slug}/"})
            if topic.get('slug') and topic.get('slug') != 'index':
                items.append({'position': 3, 'name': topic.get('name', ''), 'url': f"{base_url}/{country_slug}/{topic['slug']}/"})

        return items

    def _add_region_defaults(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Add defaults for REGION page type."""
        # Ensure related destinations exist
        if 'related_destinations' not in context:
            context['related_destinations'] = []

        # Calculate stats
        context['stats'] = {
            'vineyard_count': len(context['research'].get('vineyards', [])),
            'tasting_room_count': len(context['research'].get('tasting_rooms', [])),
            'wine_bar_count': len(context['research'].get('wine_bars', [])),
        }

        # Ensure products array exists for digital product ads
        if 'products' not in context:
            context['products'] = []

        # 24 wine topics, mobile-friendly icons + tight labels. Show ONLY the
        # topics that have real data so the hub never links to a thin/empty
        # chapter (clean nav + no thin pages). Falls back to the full nav if
        # the populated set can't be computed.
        from utils.data_loader import populated_topic_slugs as _pts
        _populated = _pts(context.get('research', {}))
        context['populated_topics'] = sorted(_populated)
        context['topic_nav'] = [t for t in WINE_TOPIC_NAV if t['slug'] in _populated] or WINE_TOPIC_NAV

        # Country-scope topic rollups: when this is a country index (no
        # region_slug), surface links to every /<country>/<topic|cuisine|
        # dish|dietary|nightlife/sub>/ page that the rollup generators
        # have actually emitted. Without this, those pages have no
        # inbound link from the parent (orphan rule violation).
        if not context.get('region_slug') and context.get('country_slug'):
            context['country_topic_rollups'] = self._country_topic_rollups(context['country_slug'])
            context['country_state_hubs'] = self._country_state_hubs(context['country_slug'])

        # City-scope price-tier rollups: when this IS a city hub
        # (region_slug present), surface chips for the cheap-eats /
        # mid-range / upscale / splurge pages emitted by
        # generate_city_price_tier.py. Same no-orphan discipline.
        if context.get('region_slug') and context.get('country_slug'):
            context['city_price_rollups'] = self._city_price_rollups(
                context['country_slug'], context['region_slug']
            )

        return context

    def _country_state_hubs(self, country_slug: str) -> list:
        """Return [{href, label}] for every state hub directly under
        /<country>/ that has an index.html. Used by region-template.html
        country-scope rendering to surface a 'By state' section so the
        state hubs aren't orphan."""
        from pathlib import Path as _P
        CONTENT_DIR = _P(__file__).resolve().parent.parent.parent / 'content'
        country_dir = CONTENT_DIR / country_slug
        if not country_dir.is_dir():
            return []
        # Anything that's neither a city (we already list those) nor a
        # known rollup slug counts as a state hub. Cities are the dirs
        # whose data/region.json exists at SITE_DATA path.
        SITE_DATA = _P(__file__).resolve().parent.parent.parent / 'site-data'
        city_slugs = {
            c.name for c in (SITE_DATA / country_slug).iterdir()
            if c.is_dir() and (c / 'data' / 'region.json').exists()
        } if (SITE_DATA / country_slug).is_dir() else set()
        rollup_slugs = {
            'restaurants', 'fine-dining', 'casual-dining', 'bakeries', 'cafes',
            'coffee-roasters', 'bars', 'wine-bars', 'breweries', 'street-food',
            'markets', 'late-night', 'hidden-gems', 'budget-eating', 'brunch',
            'food-tours', 'cooking-classes', 'day-trips-food',
            'cuisine', 'dish', 'dietary', 'nightlife',
            'cuisines', 'signature-dishes', 'neighborhoods',
        }
        out = []
        for child in sorted(country_dir.iterdir()):
            if not child.is_dir() or child.name in city_slugs or child.name in rollup_slugs:
                continue
            if (child / 'index.html').exists():
                label = child.name.replace('-', ' ').title()
                out.append({'href': f'/{country_slug}/{child.name}/', 'label': label})
        return out

    def _city_price_rollups(self, country_slug: str, city_slug: str) -> list:
        from pathlib import Path as _P
        CONTENT_DIR = _P(__file__).resolve().parent.parent.parent / 'content'
        city_dir = CONTENT_DIR / country_slug / city_slug
        if not city_dir.is_dir():
            return []
        tiers = [
            ('cheap-eats', 'Cheap Eats', '💵'),
            ('mid-range',  'Mid-Range',  '🍽️'),
            ('upscale',    'Upscale',    '✨'),
            ('splurge',    'Splurge',    '🏆'),
        ]
        out = []
        for slug, label, icon in tiers:
            if (city_dir / slug / 'index.html').exists():
                out.append({'href': f'/{country_slug}/{city_slug}/{slug}/', 'label': label, 'icon': icon})
        return out

    def _country_topic_rollups(self, country_slug: str) -> list:
        """Walk content/<country>/ and surface every rollup directory that
        actually has an index.html. Returns a flat list of
        {href, label, icon} for the country-index topic grid."""
        from pathlib import Path as _P
        CONTENT_DIR = _P(__file__).resolve().parent.parent.parent / 'content'
        country_dir = CONTENT_DIR / country_slug
        if not country_dir.is_dir():
            return []
        rollups: list[dict] = []

        # Simple food topics + nightlife umbrella: /<country>/<topic>/
        topic_labels = {
            'restaurants': ('Restaurants', '🍽️'),
            'fine-dining': ('Fine Dining', '✨'),
            'casual-dining': ('Casual', '🍴'),
            'bakeries': ('Bakeries', '🥐'),
            'cafes': ('Cafes', '☕'),
            'coffee-roasters': ('Coffee Roasters', '☕'),
            'bars': ('Bars', '🍸'),
            'wine-bars': ('Wine Bars', '🍷'),
            'breweries': ('Breweries', '🍺'),
            'street-food': ('Street Food', '🥡'),
            'markets': ('Markets', '🥬'),
            'late-night': ('Late Night', '🌙'),
            'hidden-gems': ('Hidden Gems', '💎'),
            'budget-eating': ('Budget', '💵'),
            'brunch': ('Brunch', '🥞'),
            'food-tours': ('Food Tours', '🗺️'),
            'cooking-classes': ('Cooking Classes', '👨‍🍳'),
            'day-trips-food': ('Day Trips', '🚗'),
            'nightlife': ('Nightlife', '🌃'),
        }
        for slug, (label, icon) in topic_labels.items():
            if (country_dir / slug / 'index.html').exists():
                rollups.append({'href': f'/{country_slug}/{slug}/', 'label': label, 'icon': icon})

        # Country × nightlife-sub: /<country>/nightlife/<sub>/
        nightlife_dir = country_dir / 'nightlife'
        if nightlife_dir.is_dir():
            for sub in sorted(nightlife_dir.iterdir()):
                if sub.is_dir() and (sub / 'index.html').exists() and sub.name != '':
                    # Skip the umbrella nightlife/index already linked above
                    if sub.name == 'index.html':
                        continue
                    label = sub.name.replace('-', ' ').title()
                    rollups.append({
                        'href': f'/{country_slug}/nightlife/{sub.name}/',
                        'label': label,
                        'icon': '🌃',
                    })

        # Country × cuisine: /<country>/cuisine/<x>/  (top 12 alphabetical)
        cuisine_dir = country_dir / 'cuisine'
        if cuisine_dir.is_dir():
            for sub in sorted(cuisine_dir.iterdir())[:200]:
                if sub.is_dir() and (sub / 'index.html').exists():
                    label = sub.name.replace('-', ' ').title()
                    rollups.append({
                        'href': f'/{country_slug}/cuisine/{sub.name}/',
                        'label': label,
                        'icon': '🍳',
                    })

        # Country × dish: /<country>/dish/<x>/  (top 12 alphabetical)
        dish_dir = country_dir / 'dish'
        if dish_dir.is_dir():
            for sub in sorted(dish_dir.iterdir())[:200]:
                if sub.is_dir() and (sub / 'index.html').exists():
                    label = sub.name.replace('-', ' ').title()
                    rollups.append({
                        'href': f'/{country_slug}/dish/{sub.name}/',
                        'label': label,
                        'icon': '🍲',
                    })

        # Country × dietary: /<country>/dietary/<diet>/
        dietary_dir = country_dir / 'dietary'
        if dietary_dir.is_dir():
            for sub in sorted(dietary_dir.iterdir()):
                if sub.is_dir() and (sub / 'index.html').exists():
                    label = sub.name.replace('-', ' ').title()
                    rollups.append({
                        'href': f'/{country_slug}/dietary/{sub.name}/',
                        'label': label,
                        'icon': '🥗',
                    })

        return rollups

    def _add_topic_defaults(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Add defaults for TOPIC page type."""
        # Ensure topic info exists
        if 'topic' not in context:
            context['topic'] = {
                'name': 'Attractions',
                'title': f"{context['destination']['name']} Attractions Guide 2025",
                'h1': f"{context['destination']['name']} Attractions",
                'subtitle': f"Discover the best attractions in {context['destination']['name']}",
                'read_time': 12,
                'word_count': 2500,
            }

        # Ensure sections exist
        if 'sections' not in context:
            context['sections'] = []

        # Ensure TOC exists
        if 'toc_items' not in context:
            context['toc_items'] = [
                {'id': 'overview', 'title': 'Overview'},
                {'id': 'top-attractions', 'title': 'Top Attractions'},
                {'id': 'practical-info', 'title': 'Practical Information'},
            ]

        # Ensure sidebar exists
        if 'sidebar' not in context:
            context['sidebar'] = {
                'related_topics': [],
                'quick_facts': [],
            }

        # Ensure products array exists for digital product ads on topic pages
        if 'products' not in context:
            context['products'] = []

        return context

    def _generate_default_itineraries(self, context: Dict[str, Any]) -> List[Dict]:
        """Generate default itineraries based on destination."""
        dest_name = context['destination']['name']
        return [
            {
                'title': f'5-Day {dest_name} Explorer',
                'days': [
                    {'day': 'Day 1', 'activities': f'Arrive in {dest_name}, explore city center'},
                    {'day': 'Day 2', 'activities': 'Visit top attractions and museums'},
                    {'day': 'Day 3', 'activities': 'Day trip to nearby highlights'},
                    {'day': 'Day 4', 'activities': 'Local markets and hidden gems'},
                    {'day': 'Day 5', 'activities': 'Final sightseeing, departure'},
                ]
            },
            {
                'title': f'7-Day Classic {dest_name}',
                'days': [
                    {'day': 'Days 1-2', 'activities': f'{dest_name} city highlights'},
                    {'day': 'Days 3-4', 'activities': 'Regional exploration'},
                    {'day': 'Days 5-6', 'activities': 'Cultural immersion and local experiences'},
                    {'day': 'Day 7', 'activities': 'Return and departure'},
                ]
            },
            {
                'title': f'14-Day Ultimate {dest_name}',
                'days': [
                    {'day': 'Days 1-3', 'activities': f'{dest_name} comprehensive city tour'},
                    {'day': 'Days 4-6', 'activities': 'Northern region exploration'},
                    {'day': 'Days 7-9', 'activities': 'Eastern highlights'},
                    {'day': 'Days 10-12', 'activities': 'Southern attractions'},
                    {'day': 'Days 13-14', 'activities': f'Return to {dest_name}, departure'},
                ]
            },
        ]

    def _generate_default_faqs(self, context: Dict[str, Any]) -> List[Dict]:
        """Wine-travel default FAQs. Override per-page by providing `faqs` in data.
        Replaces the TJ food-focused defaults — wine readers want to know about
        visiting cellars, harvest cadence, tasting fees and appointment policy."""
        dest_name = context['destination']['name']
        research = context.get('research', {})
        # Wine-vertical fields the agent may populate per region. Fallbacks
        # match the most common European-AOC norms; agents that fill these
        # fields per-region override the defaults.
        season = research.get('peak_wine_season',
                              'spring through autumn, with harvest the standout window')
        hours = research.get('cellar_visit_hours',
                             'most estates open 10:00 to 17:00 by appointment, often closed Sunday and Monday')
        booking_norm = research.get('booking_norm',
                                    'classified-growth and grand-cru estates require booking days to weeks ahead; smaller family domaines often take walk-ins midweek')
        tipping = research.get('tipping_norm',
                               'tipping is not expected at tastings; buying a bottle from the cellar door is the customary thank-you')

        def _strip_dot(s: str) -> str:
            return s[:-1] if isinstance(s, str) and s.endswith('.') else s

        return [
            {
                'question': f'When is the best time to visit {dest_name} for wine?',
                'answer': f'Peak wine-travel season in {dest_name} is {_strip_dot(season)}.',
            },
            {
                'question': f'Do I need an appointment to taste at {dest_name} estates?',
                'answer': f'{_strip_dot(booking_norm)}.',
            },
            {
                'question': f'What hours do {dest_name} cellars and tasting rooms keep?',
                'answer': f'{_strip_dot(hours)}.',
            },
            {
                'question': f'How does tipping work at {dest_name} tastings?',
                'answer': f'{_strip_dot(tipping)}.',
            },
            {
                'question': f'What is the one wine to try in {dest_name}?',
                'answer': self._default_must_try(context, dest_name),
            },
        ]

    @staticmethod
    def _default_must_try(context: Dict[str, Any], dest_name: str) -> str:
        # Wine-vertical: surface signature_wines first, then fall back to
        # signature_dishes (legacy from TJ) so the FAQ still reads sensibly
        # if a region happens to ship dishes but not wines yet.
        research = context.get('research', {})
        sw = research.get('signature_wines')
        if sw and isinstance(sw, list) and sw:
            first = sw[0]
            name = first.get('name') if isinstance(first, dict) else str(first)
            producer = first.get('producer_name') or first.get('producer') if isinstance(first, dict) else None
            tail = f' by {producer}' if producer else ''
            return f'If you only open one bottle, open {name}{tail}. It is the wine most associated with {dest_name}.'
        sd = research.get('signature_dishes')
        if sd and isinstance(sd, list) and sd:
            first = sd[0]
            name = first.get('name') if isinstance(first, dict) else str(first)
            return f'If you only have one meal, eat {name}. It is the dish most associated with {dest_name}.'
        return f'Ask the next local you meet what they would order. {dest_name} rewards trust.'

    @staticmethod
    def _safe_list(value, separator: str = ', ') -> str:
        """Safely render a value that may be a list or a string.
        If it's a list, join with separator. If it's a string, return as-is."""
        if isinstance(value, list):
            return separator.join(str(item) for item in value)
        return str(value) if value else ''

    @staticmethod
    def _format_price_range(value, default: str = 'Contact for pricing') -> str:
        """Format a price_range that may be a dict or string.

        Handles:
        - Dict with low_season/high_season: renders as "low_season. high_season"
        - Dict with low/high: renders as "low. high"
        - String: returns as-is
        - None/empty: returns default
        """
        if not value:
            return default
        if isinstance(value, dict):
            low = value.get('low_season') or value.get('low') or ''
            high = value.get('high_season') or value.get('high') or ''
            if low and high:
                return f"{low} to {high}"
            elif low:
                return low
            elif high:
                return high
            return default
        return str(value)

    @staticmethod
    def _slugify(text: str) -> str:
        """Convert text to URL-safe slug."""
        text = text.lower().strip()
        text = re.sub(r'[^\w\s-]', '', text)
        text = re.sub(r'[\s_]+', '-', text)
        return text

    @staticmethod
    def _striptags(text: str) -> str:
        """Remove HTML tags from text."""
        return re.sub(r'<[^>]+>', '', str(text))

    @staticmethod
    def _truncate_words(text: str, length: int = 50) -> str:
        """Truncate text to specified number of words."""
        words = str(text).split()
        if len(words) <= length:
            return text
        return ' '.join(words[:length]) + '...'

    @staticmethod
    def _price_to_int(entity) -> int | None:
        """Best-effort numeric price for sort widgets. Returns None when
        the entity has no price-shaped fields at all (so the sort filter
        can skip emitting data-price).

        Strategy:
          1. price_range / price / tasting_menu_price -> first integer found
             ("$45", "€30-50", "180 EUR" -> 45 / 30 / 180)
          2. price_tier (e.g. "$$", "€€€") -> char count × 30 to put it on
             roughly the same scale as numeric prices (tier-2 ~= $60).
          3. Nothing parseable -> None.
        """
        import re
        if not isinstance(entity, dict):
            return None
        for field in ("price_range", "price", "tasting_menu_price"):
            raw = entity.get(field)
            if isinstance(raw, str) and raw.strip():
                m = re.search(r"\d+", raw.replace(",", ""))
                if m:
                    return int(m.group(0))
        tier = entity.get("price_tier")
        if isinstance(tier, str) and tier.strip():
            # Count consecutive currency-sigil chars at the start.
            sigils = sum(1 for c in tier if c in "$€£¥₩₹฿")
            if sigils:
                return sigils * 30
        return None

    @staticmethod
    def _humanize_duration(iso: str) -> str:
        """Convert ISO 8601 duration (PT1H30M, PT45M) to short human form ("1 hr 30 min", "45 min")."""
        if not iso or not isinstance(iso, str):
            return ''
        m = re.match(r'^PT(?:(\d+)H)?(?:(\d+)M)?$', iso.strip())
        if not m:
            return iso
        hours = int(m.group(1)) if m.group(1) else 0
        mins = int(m.group(2)) if m.group(2) else 0
        parts = []
        if hours:
            parts.append(f"{hours} hr")
        if mins:
            parts.append(f"{mins} min")
        return ' '.join(parts) if parts else iso


def render_page(site_data: Dict[str, Any], page_type: str = 'REGION', templates_dir: str = None, topic_slug: str = None) -> str:
    """
    Convenience function to render a page.

    Args:
        site_data: Site-data dictionary
        page_type: 'REGION' or 'TOPIC'
        templates_dir: Optional path to templates directory
        topic_slug: For TOPIC pages, the specific topic (e.g., 'attractions', 'hotels')
                   to use topic-specific templates

    Returns:
        Rendered HTML string
    """
    renderer = TemplateRenderer(templates_dir)
    return renderer.render(site_data, page_type, topic_slug)
