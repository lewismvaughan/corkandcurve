# QA1 Report — portugal/douro (Cork & Curve)

- Date: 2026-05-25
- Agent: QA1 (judgment pass, PROMPT.md sections A-F + L)
- Inputs: vineyards.json (33 estates), wines.json (94 cuvées), signature-wines.json (12), + topic files for address cross-check
- ship_safety on entry: PASS (0 HARD, 7 layers). ship_safety after QA edits: ALL CHECKS PASSED (0 HARD).
- Total defects fixed: 4 (all score-citation; 3 in wines.json, 2 prose mirrors in signature-wines.json — counted as 4 distinct defects)

---

## Section A — Classification accuracy  →  PASS (0 defects)

The region carries two DOCs: fortified Port = **DOC Porto**, still wine = **DOC Douro**. Verified across vineyards + wines + signature-wines.

- `wines[*].classification` takes exactly two values: `DOC Porto` (62) and `DOC Douro` (32). No `DOCa` (Spain), no `AOC` (France), no IGT/DOCG.
- Port STYLE names (Vintage / LBV / Tawny / Colheita / Ruby / White / Rosé) do NOT appear in any `classification` field. Style is carried in `wines[*].style` using the controlled WINE_TAGS vocab (`fortified-port`, `fortified-vdn`, `still-red`, `still-white`), which is correct.
- vineyards.json classifications are all `DOC Porto`, `DOC Douro`, or both (dual-licence estates such as Quinta do Noval, Crasto, Vale Meão, Niepoort) — legitimate, since these estates bottle both Port and still Douro wine.
- Sampled ~20 entities across the three files; 0 classification defects, so no broadening required.
- Note (non-defect): signature-wines.json uses free-prose `style` strings like "Vintage Port" / "still red DOC Douro". These are a separate descriptive field, not the validated `classification` field, so not in scope of the A defect class.

## Section B — Hectarage realism  →  PASS (0 defects)

Five vineyards carry a `hectares` claim. All verified against producer / independent data, and all correctly use the PLANTED-vineyard figure rather than the total-estate figure:

| Estate | data `hectares` | Verified | Source note |
|---|---|---|---|
| Quinta do Noval | 145 | 145 ha (classified letter A) | worldsbestvineyards / wineanorak — Nacional block ~2.5 ha within |
| Quinta do Crasto | 74 | 74 ha planted (135 ha estate) | worldsbestvineyards / winery |
| Quinta do Vale Meão | 62 | 62 ha vines (270 ha historic estate) | producer / multiple; description correctly cites 270 as the 1877 land purchase, not as vine area |
| Quinta do Vesúvio | 133 | 133 ha planted (326 ha estate) | Symington — exact planted figure, not the 326 total |
| Quinta da Romaneira | 85 | consistent (≈400 ha estate, ~85 ha vines) | planted-vs-total distinction handled correctly in prose |

No fabricated or estate-vs-vineyard-confused figures found.

## Section C — Score citations  →  4 defects, all CORRECTED

### C2 — every score with points >= 99 (numeric tuple verification)

Three >=99 tuples existed. All three source-verified:

1. **quinta-do-noval-nacional — Wine Advocate 100 / vintage 2011 / review 2013** — VERIFIED REAL. The 2011 Nacional Vintage Port scored a perfect 100 from The Wine Advocate (Neal Martin / Mark Squires), drink window 2045-2080. KEPT unchanged.

2. **dows-vintage — Wine Spectator 99 / vintage 2016 / review 2018** — DEFECT (inflated). Verified WS published score for the 2016 Dow's Vintage Port is **98**, not 99 (corroborated by multiple retailers quoting the WS note verbatim; Vinous and Decanter also 98). This is the exact C2 fingerprint (99-claim where published was 98).
   - FIX: `points` 99 → 98 in wines.json.
   - FIX: signature-wines.json `tasting_notes` prose "Wine Spectator 99 points 2016 vintage" → "98 points".

3. **quinta-do-noval-nacional — Wine Spectator 99 / vintage 1994 / review 1997** — DEFECT (misattributed publication). The 99-point score for the 1994 Nacional belongs to **Robert Parker / The Wine Advocate** (confirmed via tastingbook: "99 pts Robert Parker"). Wine Spectator actually scored the 1994 Nacional 100, so the (reviewer=Wine Spectator, points=99) tuple is wrong on both axes.
   - FIX: `reviewer` "Wine Spectator" → "Robert Parker (Wine Advocate)" in wines.json (points 99, vintage 1994 retained — that tuple is the verified one).

### C (sub-99 structural) — additional correction

4. **ferreira-barca-velha — Wine Advocate 98 / vintage 2011 / review 2021** — DEFECT (inflated by 1). Verified WA published score for the 2011 Barca Velha is **97** (winewatch quotes "97 points — Wine Advocate"; James Suckling separately gave 99, but that is a different publication not claimed here). Although 97/98 is below the C2 mandatory-verification threshold, the wine is an editorial 5.0 flagship cited in signature prose, so corrected for credibility.
   - FIX: `points` 98 → 97 in wines.json.
   - FIX: signature-wines.json prose "Wine Advocate 98 points 2011 vintage" → "97 points".

### Score completeness (all 111 score entries)

All entries carry reviewer + points + vintage + year. 38 entries have `vintage: 0` — every one is a genuinely non-vintage style (aged Tawny, Colheita, Reserve, White Port, Rosé, Moscatel). `vintage: 0` is the correct NV encoding; confirmed zero `vintage: 0` entries sit on a Vintage Port or still red (where a vintage is mandatory). Not a defect.

## Section F — Independent-directory address cross-check  →  PASS (0 fabrications)

Spot-checked addresses via independent sources (Google Maps / winery / Falstaff / worldsbestvineyards / trade directories):

- **Quinta do Crasto** — Gouvinhas, 5060-063 Sabrosa: confirmed exact.
- **Niepoort** — Rua Cândido dos Reis 598, 4400-071 Vila Nova de Gaia: confirmed exact. The earlier sibling-agent flag (address set to "Quinta de Napoles") is RESOLVED — current data carries the correct Gaia lodge address and the `address_quoted` matches.
- **Quinta do Noval** — Vale de Mendiz, 5085-110 Pinhão: confirmed.
- **Quinta do Vale Meão**, **Quinta do Vesúvio** — confirmed via producer/Symington.
- Spot-checked Taylor's, Graham's, Sandeman, Kopke, Ferreira Gaia addresses against producer contact pages — all street-level and consistent.
- `open_status` audited across all vineyards: every value is `open` (within the allowed enum {open, seasonal, unknown, permanently_closed}).

**Quinta de Roriz / Chryseia note (borderline, NOT fixed):** the `chryseia` vineyard record uses `address: "Quinta de Roriz, Ervedosa do Douro, São João da Pesqueira, Cima Corgo"` with `address_quoted: "Quinta de Roriz"`. These are rural Douro quintas with no street-level postal address; the named estate IS the locatable address (confirmed real: Quinta de Roriz, parish of São João da Pesqueira, near Ervedosa, acquired by Prats & Symington from the van Zeller family in 2009). `address` and `address_quoted` are mutually consistent and ship_safety's addr fuzzy-match passes. The earlier sibling-agent "Quinta de Roriz addr_mismatch" flag is RESOLVED. Left as-is — this is a real named estate, not a bare town/appellation, and no finer street address is verifiable.

## Section L — Cuvée → producer & signature → cuvée cross-reference  →  PASS (0 defects)

- All 94 `wines[*].producer` slugs resolve to a `vineyards[*].slug`. 0 orphans.
- All 12 `signature_wines[*].slug` exist in `wines[*].slug`. 0 orphans.
- All 12 `signature_wines[*].producer` resolve in vineyards.json.
- Section K bonus: no `wines[*].slug` or `wines[*].name` contains a 4-digit vintage year (vintage-agnostic discipline holds).

## Section J (tag vocab, build-breaking — checked opportunistically)  →  PASS

Every tag in `wines[*].tags` appears in docs/WINE_TAGS.md. No derived-axis tags (price-*, grape, world, ageing, production) leaked into researcher-emitted `tags[]`.

---

## Files modified

- `site-data/portugal/douro/data/wines.json` — 3 score corrections (dows-vintage WS 99→98; quinta-do-noval-nacional 1994 reviewer Wine Spectator→Robert Parker (Wine Advocate); ferreira-barca-velha WA 98→97)
- `site-data/portugal/douro/data/signature-wines.json` — 2 prose corrections mirroring the dows-vintage and barca-velha score fixes

## Post-edit verification

- All three edited JSON files parse cleanly.
- `bash scripts/ship_safety.sh portugal douro` → ALL CHECKS PASSED (0 HARD). The single transient 502 on the WSET wine-school booking URL (wow.pt) re-checked as live 200 (3/3) and is unrelated to QA edits.
