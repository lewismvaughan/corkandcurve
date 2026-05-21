#!/usr/bin/env python3
"""One-off: fix HARD address-mismatch + dead-source issues in Charleston.
Atomic writes via os.replace. Run once, then delete."""
import json, os, tempfile
from pathlib import Path

ROOT = Path("/station/repo/site-data/united-states/charleston/data")

def atomic_write(path: Path, data):
    with tempfile.NamedTemporaryFile("w", delete=False, dir=path.parent,
                                     prefix=path.name, suffix=".tmp",
                                     encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
        tmp = f.name
    os.replace(tmp, path)

def patch_entity(file_name, top_key, finder, patches, dict_key=None):
    """finder: callable(entity) -> bool. patches: dict of edits to apply.
    If dict_key set, finder applies to entities under data[top_key][dict_key]."""
    path = ROOT / file_name
    data = json.loads(path.read_text(encoding="utf-8"))
    if dict_key:
        entries = data[top_key][dict_key]
    else:
        entries = data[top_key]
    n_hits = 0
    for e in entries:
        if not finder(e):
            continue
        for k, v in patches.items():
            if "." in k:
                parts = k.split(".")
                target = e
                for p in parts[:-1]:
                    target = target.setdefault(p, {})
                target[parts[-1]] = v
            else:
                e[k] = v
        n_hits += 1
    if n_hits == 0:
        raise SystemExit(f"NO HIT: {file_name} {top_key}")
    atomic_write(path, data)
    print(f"  patched {file_name} ({n_hits} entry/entries)")

# ---- breweries.json ----
# edmunds-oast-brewing: add Ste 115 to entity.address
patch_entity("breweries.json", "breweries",
    lambda e: e.get("slug") == "edmunds-oast-brewing",
    {"address": "1505 King St Ste 115, North Charleston, SC 29405"})

# cooper-river-brewing: switch to working source, update quoted+entity address
patch_entity("breweries.json", "breweries",
    lambda e: e.get("slug") == "cooper-river-brewing",
    {
        "address": "2201B Mechanic Street, North Charleston, SC 29405",
        "verified.source_url": "https://charlestonbrewerydistrict.com/98-cooper-river-brewing",
        "verified.address_quoted": "2201B Mechanic Street, North Charleston 29405, South Carolina, United States",
        "verified.open_evidence_url": "https://charlestonbrewerydistrict.com/98-cooper-river-brewing",
        "verified.cuisine_evidence_url": "https://charlestonbrewerydistrict.com/98-cooper-river-brewing",
        "verified.checked_on": "2026-05-19",
    })

# ---- cafes.json ----
# the-daily-king: update quoted to match the actual page text ("652 B King Street")
patch_entity("cafes.json", "cafes",
    lambda e: e.get("slug") == "the-daily-king",
    {
        "verified.address_quoted": "652 B King Street Charleston, SC 29403",
        "verified.checked_on": "2026-05-19",
    })

# ---- coffee-roasters.json ----
# the-daily-king: same
patch_entity("coffee-roasters.json", "coffee_roasters",
    lambda e: e.get("slug") == "the-daily-king",
    {
        "verified.address_quoted": "652 B King Street Charleston, SC 29403",
        "verified.checked_on": "2026-05-19",
    })

# ---- casual-dining.json ----
# xiao-bao-biscuit
patch_entity("casual-dining.json", "casual_dining",
    lambda e: e.get("slug") == "xiao-bao-biscuit",
    {
        "address": "224 Rutledge Ave, Charleston, 29403",
        "verified.address_quoted": "224 Rutledge Ave., Charleston, 29403, United States",
    })

# page-s-okra-grill (note: hyphenated slug)
patch_entity("casual-dining.json", "casual_dining",
    lambda e: e.get("slug") == "page-s-okra-grill",
    {
        "address": "302 Coleman Blvd, Mt. Pleasant, SC 29464",
    })

# rodney-scotts-bbq: change to drop SC to match Michelin quoted format
patch_entity("casual-dining.json", "casual_dining",
    lambda e: e.get("slug") == "rodney-scotts-bbq",
    {
        "address": "1011 King Street, Charleston, 29403",
    })

# ---- restaurants.json ----
# verns: switch source to own site
patch_entity("restaurants.json", "restaurants",
    lambda e: e.get("slug") == "verns",
    {
        "address": "41 Bogard Street, Charleston, SC 29403",
        "verified.source_url": "https://www.vernschs.com/",
        "verified.address_quoted": "41 BOGARD STREET CHARLESTON, SC 29403",
        "verified.checked_on": "2026-05-19",
    })

# the-obstinate-daughter (restaurants + fine-dining)
patch_entity("restaurants.json", "restaurants",
    lambda e: e.get("slug") == "the-obstinate-daughter",
    {"address": "2063 Middle Street, Sullivan's Island, SC"})

# sullivans-fish-camp
patch_entity("restaurants.json", "restaurants",
    lambda e: e.get("slug") == "sullivans-fish-camp",
    {"address": "2019 Middle Street, Suite A, Sullivan's Island, SC 29482"})

# estadio (restaurants)
patch_entity("restaurants.json", "restaurants",
    lambda e: e.get("slug") == "estadio",
    {"address": "122 Spring Street, Charleston, SC"})

# xiao-bao-biscuit (restaurants)
patch_entity("restaurants.json", "restaurants",
    lambda e: e.get("slug") == "xiao-bao-biscuit",
    {"address": "224 Rutledge Ave, Charleston, 29403"})

# pages-okra-grill (note: different slug here than casual-dining)
patch_entity("restaurants.json", "restaurants",
    lambda e: e.get("slug") == "pages-okra-grill",
    {"address": "302 Coleman Blvd, Mt. Pleasant, SC 29464"})

# ---- fine-dining.json ----
patch_entity("fine-dining.json", "fine_dining",
    lambda e: e.get("slug") == "verns",
    {
        "address": "41 Bogard Street, Charleston, SC 29403",
        "verified.source_url": "https://www.vernschs.com/",
        "verified.address_quoted": "41 BOGARD STREET CHARLESTON, SC 29403",
        "verified.checked_on": "2026-05-19",
    })

patch_entity("fine-dining.json", "fine_dining",
    lambda e: e.get("slug") == "the-obstinate-daughter",
    {"address": "2063 Middle Street, Sullivan's Island, SC"})

patch_entity("fine-dining.json", "fine_dining",
    lambda e: e.get("slug") == "sullivans-fish-camp",
    {"address": "2019 Middle Street, Suite A, Sullivan's Island, SC 29482"})

# ---- wine-bars.json ----
patch_entity("wine-bars.json", "wine_bars",
    lambda e: e.get("slug") == "estadio",
    {"address": "122 Spring Street, Charleston, SC"})

# ---- bars.json ----
# Proof rebranded to 100 Proof Oct 2024; use Commonwealth Company landlord page as source
patch_entity("bars.json", "bars",
    lambda e: e.get("slug") == "proof",
    {
        "name": "100 Proof",
        "description": "100 Proof in Charleston is the rebrand of long-running King Street cocktail bar Proof since October 2024. The kitchen runs 100 shots, frosé and craft cocktails from the original team.",
        "verified.source_url": "https://thecommonwealthcompany.com/proof-bar/",
        "verified.address_quoted": "437 King Street, Charleston SC 29403",
        "verified.open_evidence_url": "https://thecommonwealthcompany.com/proof-bar/",
        "verified.cuisine_evidence_url": "https://thecommonwealthcompany.com/proof-bar/",
        "verified.checked_on": "2026-05-19",
    })

# ---- festivals.json ----
# charleston-wine-and-food: quoted matches Marion Square reference
patch_entity("festivals.json", "food_festivals",
    lambda e: e.get("slug") == "charleston-wine-and-food",
    {"meeting_point": "Marion Square, Charleston, SC (and multiple downtown venues)"})

# lowcountry-oyster-festival: address_quoted "Boone Hall Plantation & Gardens"
patch_entity("festivals.json", "food_festivals",
    lambda e: e.get("slug") == "lowcountry-oyster-festival",
    {
        "meeting_point": "Boone Hall Plantation & Gardens, 1235 Long Point Rd, Mount Pleasant, SC",
        "verified.open_evidence_url": "https://www.lowcountryhospitalityassociation.com/lowcountry-oyster-fest/",
    })

# spoleto-festival-usa
patch_entity("festivals.json", "food_festivals",
    lambda e: e.get("slug") == "spoleto-festival-usa",
    {"meeting_point": "Charleston, SC (venues across historic downtown)"})

# charleston-restaurant-week
patch_entity("festivals.json", "food_festivals",
    lambda e: e.get("slug") == "charleston-restaurant-week",
    {"meeting_point": "Charleston, SC (participating restaurants citywide)"})

# second-sunday-on-king
patch_entity("festivals.json", "food_festivals",
    lambda e: e.get("slug") == "second-sunday-on-king",
    {"meeting_point": "King Street, Charleston, SC (between Queen and Calhoun)"})

print("PHASE-1 HARD fixes done.")
