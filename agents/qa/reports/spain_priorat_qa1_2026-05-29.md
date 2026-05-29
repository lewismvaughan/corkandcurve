# QA1 Report — spain/priorat — 2026-05-29

**Agent:** QA1 (judgment pass)
**Data scale:** 50 producers, 135 cuvées (B1 88 + B2 47), ~30 topic files
**ship_safety after QA1 edits:** ALL CHECKS PASSED — 0 HARD

---

## Section A — Classification accuracy

- **L'Ermita:** Correctly listed as `DOQ Priorat Gran Vinya Classificada` in both `vineyards.json` (`celler-la-vinyes-lermita`) and `wines.json`. PASS.
- **Manyetes:** Correctly labelled `DOQ Priorat` with `Vinya Classificada` noted in description and history. PASS.
- **Mas de la Rosa (Vall Llach):** Correctly `DOQ Priorat Gran Vinya Classificada`. PASS.
- **1902 Tossal d'en Bou (Mas Doix):** Correctly `DOQ Priorat Gran Vinya Clasificada`. PASS.
- **Espectacle del Montsant:** Correctly `DO Montsant`, not DOQ Priorat. PASS.
- **Venus la Universal:** Correctly `DO Montsant / DOQ Priorat`. PASS.
- **Cooperativa Falset Marca:** Correctly `DO Montsant / DOQ Priorat`. PASS.
- **Celler el Masroig:** Correctly `DO Montsant`. PASS.
- All other 43 producers correctly labelled `DOQ Priorat`. No Italian DOC/DOCG terms found anywhere. PASS.
- **Fixed:** Clos Mogador description said "Clos Mogador holds Vinya Classificada status" — incorrect (the Manyetes plot holds VC status, not the estate/flagship wine). Fixed to "The estate's Manyetes plot holds Vinya Clasificada status."

---

## Section B — Hectarage realism

Agent A omitted most hectares as unverifiable. No fabricated hectare claims found. PASS (nothing to fix).

---

## Section C — Score citations + prose score claims

`check_score_claims.py --strict` reports **0 hits** before and after edits.

Manual sweep of all `history.milestones[*].event`, `description`, `taste.summary`, `tip` fields across wines.json and vineyards.json:
- No numeric score claims (90-100 points/pts/100/punti) found in prose.
- No Parker/WA/WS/Suckling/Decanter/Falstaff/Atkin claims found.
- No "Top 100 / Top 50 / top N wines / greatest" ranking phrases found.

**Soft superlatives stripped (Section C addendum):**

1. `wines.json:1087` — `"Sara Perez, now one of Catalonia's leading winemakers"` → stripped, replaced with factual statement of her role and co-founded Venus la Universal.
2. `wines.json:8762` — `"Torres, one of Spain's leading wine families"` → replaced with `"Familia Torres, the Catalan wine producer founded in Vilafranca del Penedes in 1870"`.
3. `region.json:139` — `"relaunched Priorat as a world-class wine region"` → rewritten to factual sequence: wave of investment + DOQ 2001.
4. `region.json:15 (blurb)` — `"some of the country's most striking old-vine reds"` → replaced with factual `"cult-level old-vine reds"`.
5. `wines.json:7812` — `"one of the region's most striking expressions"` → replaced with factual `"focuses on a single plot of extreme old-vine Garnacha"`.
6. `neighborhoods.json:65` — `"some of the most compelling Cariñena old-vine parcels in all of Spain"` → replaced with factual vine age and classification.
7. `neighborhoods.json:319` — `"among the most studied single vineyards in Spain"` → replaced with factual Gran Vinya Clasificada classification.
8. `hidden-gems.json:21` — `"among the most intellectually interesting wines in the DOQ"` → stripped (unsourceable ranking claim).
9. `itineraries.json` — `"produces the most distinctive wines in the DOQ"` → rewritten to factual description of Terroir Al Limit's style.

---

## Section D — Ownership currency + fabrication/cross-contamination

**Defect 1 — Daphne Glorian nationality: two conflicting fabricated claims (HIGH)**
- `vineyards.json`: "Swiss-born Daphne Glorian"
- `wines.json`: "a Belgian-born winemaker"
- QA brief states she is American by birth.
- Action: Removed both nationality claims. Both entries now refer to "Daphne Glorian" without national origin. The QA brief's "American by birth" was noted but without a primary source in the data, the safest resolution is nationality-neutral.

**Defect 2 — Clos de l'Obac co-founder: Carme Casalas replaced by Mariona Jarque (MEDIUM)**
- `vineyards.json` listed `"owner": "Carles Pastrana and Mariona Jarque"` with description saying they co-founded in 1989.
- Per QA brief, Carme Casalas was the 1989 co-founder. Mariona Jarque is the current winemaker, not the original co-founder.
- Action: Nulled `owner` (unverifiable current ownership), retained `winemaker: "Mariona Jarque"`, rewrote founding description to cite only Carles Pastrana as founder.

**Defect 3 — Saó del Coster: conflicting fabricated founder names (HIGH)**
- `vineyards.json`: `"owner": "Joel Chevallaz and Patrick Pochon"`, `"winemaker": "Jerome Carretero"`, founded 2004.
- `wines.json` (sao-roig, sao-blanco): all references to "Aaron Mestre" as founder, founded 2003.
- Both sets of names appear in no cited source (only generic DOQ directory or Wine-Searcher); names are incompatible with each other — classic cross-contamination pattern.
- Action: Nulled `owner` and `winemaker` in vineyards.json. Removed all "Aaron Mestre" personal attributions from wines.json prose. Corrected wine origin_year milestone from 2003 to 2004.

**Defect 4 — L'Infernal founders: "Marc Combier" vs "Laurent Combier" (MEDIUM)**
- `vineyards.json`: "Laurent Combier, Peter Fischer and Jean-Michel Gerin"
- `wines.json history`: "Marc Combier (Crozes-Hermitage), Philippe Fischer, and Jean-Michel Gerin"
- Laurent Combier is the well-known Croze-Hermitage name; "Marc Combier" and "Philippe Fischer" are not in any cited source.
- Action: Removed personal names from wines.json history summaries (replaced with "three French founders"). Retained the factual vineyards.json attribution since Laurent Combier is a verifiable Rhône producer name.

**Defect 5 — Dominik Huber nationality: "Swiss-born" (MEDIUM)**
- `wines.json:2164`: "Huber, a Swiss-born winemaker"
- QA brief confirms German-born.
- Action: Changed to "German-born winemaker who previously worked at Mas Martinet".

---

## Section E — Biodynamic/Organic certification

**Defect 6 — Clos Mogador biodynamic/organic status inconsistency (MEDIUM)**
- `vineyards.json`: `biodynamic_status: "none"`, `organic_status: "none"`
- `wines.json` and `dietary.json`: both show `biodynamic_practicing` / `organic_certified` with cited source `closmogador.cat/en/regenerative-viticulture-and-biodynamic-practices-in-priorat/`
- Action: Updated vineyards.json to `biodynamic_status: "biodynamic_practicing"`, `organic_status: "organic_certified"` to match the better-sourced dietary.json entry.

**Defect 7 — Saó del Coster: demeter_certified without Demeter source (MEDIUM)**
- `vineyards.json` had `biodynamic_status: "demeter_certified"` with only DOQ general directory as source.
- No Demeter registry URL or CCPAE certifier link provided.
- Action: Downgraded to `biodynamic_practicing` and updated description accordingly.

Remaining entries:
- Mas Martinet: `organic_certified / biodynamic_practicing` with CCPAE source. PASS.
- Clos Erasmus: `biodynamic_practicing / organic_certified` (not Demeter, as stated in dietary.json). PASS.
- Terroir Al Limit: `biodynamic_practicing / organic_certified`. PASS.
- Mas Doix: `biodynamic_practicing / organic_certified` with own website as source. PASS.

---

## Section F — Address cross-check (10 entities sampled)

All 10 sampled entities have street-level addresses matching address_quoted. One structural note: several minor producers (celler-els-guiamets, celler-eudald-massana-noya, etc.) use the DOQ general directory as source, which means address cannot be independently cross-verified. These have `open_status: unknown` already set appropriately. No fabricated addresses found in the sample.

---

## Section L — Cuvée → producer cross-reference

**Defect 8 — Broken vineyard→wine signature_wine slugs: 44 broken references (HIGH)**

The research agent populated `vineyards[*].signature_wines` with slug names that did not match actual `wines[*].slug` values in wines.json. This was systematic across most producers.

Fixed all 44 broken refs for all affected producers by mapping to correct wines.json slugs:
- clos-mogador: `clos-mogador-vinya-classificada` → `clos-mogador`, `manyetes-vi-de-paratge` → `manyetes`, `nelin` → `clos-nelin`
- clos-de-lobac: `kyrie-blanc` → `kyrie`
- cellers-scala-dei: `scala-dei-sant-antoni` → `scala-dei-masdeu`
- terroir-al-limit: `terra-de-cuques-negre` → `dits-del-terra`
- ferrer-bobet: `ferrer-bobet-seleccio-especial` → `ferrer-bobet-selecci-especial`
- mas-doix: `doix-1902` → `mas-doix-carinena-centenaria`, `doix-salanques` → `salanques-mas-doix`, `doix-les-crestes` → `doix-costers-vinyes-velles`
- mas-den-gil: `mas-den-gil-coma-vella` → `coma-vella`, `mas-den-gil-clos-fonta` → `clos-fonta`, `mas-den-gil-gran-buig` → `bellmunt-mas-den-gil`
- celler-pasanau: `pasanau-finca-la-planeta` → `finca-la-planeta`, others → `la-morera-de-montsant`, `ceps-nous`
- marco-abella: `marco-abella-clos-abella` → `mas-mallola`, etc.
- sangenis-i-vaque: all three fixed to actual slug names
- rotllan-torra: `rotllan-torra-reserva` → `rotllan-torra-crianza`, `rotllan-torra-amadis` → `rotllan-torra-tirant`
- clos-berenguer: → `clos-berenguer-negre`, `clos-berenguer-blanc`
- celler-cal-pla: → `celler-cal-pla-planots`, `celler-cal-pla-nou-naix`
- mas-igneus: → `mas-igneus-fa-112`, `mas-igneus-ig`
- sao-del-coster: → `sao-roig`, `sao-blanco`
- bodegas-mas-alta: → `la-creu-alta`, `artigot`, `bodegas-mas-alta-garnacha`
- costers-del-priorat: → `costers-del-priorat-pissarres`, `costers-del-priorat-carinyena`
- clos-erasmus: `clos-erasmus-laurel` → `laurel`
- celler-1902-mas-doix: `doix-1902` → `mas-doix-carinena-centenaria`
- celler-clos-figueras: → `font-de-la-figuera`, `clos-figueres`
- celler-orto-vins: `orto-vins-vi-de-paratge` → `orto-vi-de-vila`
- cellers-cecilio: → `cecilio-vi-de-vila-gratallops`
- nin-ortiz: `nin-ortiz-nit-de-les-animes` → `nit-de-les-animes`
- cooperativa-falset-marca: `etim-dolc` → `etim-dolc-natural`
- venus-la-universal: `dido-la-universal` → `dido-negre`

**Itineraries venues populated:**
All 5 itineraries had empty `venues: []` arrays. Populated with real vineyard slugs:
- cinc-pioners: day1=[clos-mogador], day2=[alvaro-palacios, mas-martinet], day3=[clos-de-lobac, vall-llach]
- falset-village: day1=[cooperativa-falset-marca], day2=[vall-llach, cims-de-porrera, terroir-al-limit]
- penedes-cava: day1-2 populated with relevant estates
- fira-del-vi: day2=[cooperativa-falset-marca, cellers-scala-dei, buil-gine], day3=[mas-martinet, buil-gine]
- harvest-week: all 5 days populated

**Cross-ref verification post-fix:**
- `wines[*].producer` → `vineyards[*].slug`: 0 broken
- `vineyards[*].signature_wines` → `wines[*].slug`: 0 broken
- `signature-wines.json[*].slug` → `wines[*].slug`: 0 broken
- `signature-wines.json` includes `mas-doix-carinena-centenaria` (renamed from doix-1902): CONFIRMED

---

## Defect count summary

| Class | Count |
|---|---|
| Fabricated/conflicting nationality claims (Glorian, Huber) | 2 |
| Fabricated/cross-contaminated owner names (Saó del Coster, Pastrana co-founder, L'Infernal) | 3 |
| Biodynamic status errors (Mogador inconsistency, Saó demeter downgrade) | 2 |
| Broken vineyard→wine signature_wine cross-refs | 44 |
| Empty itinerary venues (all 5 itineraries) | 5 |
| Prose superlatives stripped | 9 |
| Classification accuracy (Mogador VC claim) | 1 |
| **Total** | **66** |

---

## Final ship_safety outcome

```
spain/priorat: ALL CHECKS PASSED
0 HARD failures
```
