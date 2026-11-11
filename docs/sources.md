# Sources, reconciliation and coverage

Snapshot audited 2026-11-10. Latest observed map date: 2026-11-04. **Partial career coverage; no claim of completeness.**

| Data layer | Accepted maps | Identity | Provenance / license |
|---|---:|---|---|
| Historical base | 1,297 | HLTV player 3741 + player link | Filipe Macedo, Counter Strike Competitive Data v1, CC BY 4.0 |
| Historical gap | 157 | Exact NiKo / G2 / date window | tedtay CS-GO-Pro-Matches-Comprehensive-Dataset; repository declares MIT |
| CS2 provider maps | 542 | Provider player 26, full name Nikola Kovač, country BA | Maxim / ektarr, Counter-Strike Pro Matches v10, CC BY-SA 4.0 |
| History-only CS2 observations | 34 | HLTV history page 3741 | HLTV public history excerpt |

Final accepted totals: 2,030 maps. CS2: G2 195 maps, Falcons 381 maps. Provider supplied 543 candidate maps; one conflicting candidate is quarantined. Recent HLTV displayed Rating is also attached to 231 matched provider observations, not added as extra maps.

## Original base recovered and verified

Original URL: https://www.kaggle.com/datasets/filipechavesdemacedo/counter-strike-competitive-data

Author: Filipe Macedo. Kaggle v1, updated 2021-06-24. Public API metadata declares Attribution 4.0 International (CC BY 4.0). All three downloaded archive files matched local files byte-for-byte by SHA-256 on 2026-11-10. Hashes and source metadata are preserved in `data/provenance/sources.json`.

Previously missing original provenance is now resolved. The base is a filtered derivative of the original source, not a new scrape. Preserve author/source/license attribution.

## Added CS2 dataset

URL: https://www.kaggle.com/datasets/ektarr/counter-strike-pro-matches

Author: Maxim (ektarr). Version 10, updated 2026-11-07. Public API metadata declares CC BY-SA 4.0. Processed derivative: `data/processed/niko_ektarr_cs2_v10.csv`. Input archive has 24,001 rows, containing both map observations and series totals. The importer requires `is_total == False`, and uses provider-specific map/player keys. It does not treat series totals as maps.

The provider player table resolves ID 26 to `NiKo (Nikola Kovač), BA`; ID 153 is `niko (Nikolaj Kristensen), DK` and is excluded. These IDs are provider-specific: do not replace HLTV ID 3741 with 26. The provider's own player/map/series IDs are preserved in dedicated fields. No HLTV map-ID claim is made.

Provider NiKo map coverage: G2, 2023-11-30–2024-12-14 (195 candidates); Falcons, 2025-01-15–2026-11-04 (348 candidates). The dataset supplies kills, deaths, assists, ADR, KAST, map scores, tournament and source datetime; **it does not supply Rating**. Missing Rating remains missing unless independently joined to a matching history record.

## Cross-source reconciliation

HLTV inputs are factual observations extracted from readable results for the NiKo player-history page and offsets 100 and 200. Raw HTML was not available; the original factual excerpt remains in `hltv_recent_rows.json` and `niko_maps_before_cs2.csv`.

- 231 exact date/team/opponent/map keys match K/D and map score: add the displayed Rating and retain the rating source URL.
- 1 exact key conflicts on K/D: 2026-03-20, Falcons vs Natus Vincere, Dust2. Old excerpt says 14/14; provider says 12/13. Both observations for this key are quarantined from analysis until verified on a primary scoreboard.
- 10 old excerpt observations match combat counts and scores within one day but differ in date: remove those old observations from analysis and retain provider records. No guessed date shift or additional Rating join is made.
- 34 history observations have no exact provider match and remain as history-only observations, with missing ADR/assists/KAST.

Every decision is logged in `reports/cs2_reconciliation.csv`. Canonical joins require uniqueness; ambiguous same-day keys fail rather than multiply rows. Team normalization removes `Team` / `Esports` wrappers for joins. This is a namespace reconciliation rule, not proof that all renamed organizations are equivalent.

The 276 original webpage observations were partial excerpts, not a random sample. Cached pages reported different total career counts. Dataset dates can represent source match dates; these have not been converted to a claimed user-local timezone. Accepted combined coverage is not a certified complete match census.

## Rating policy and analysis

Legacy rating versions are date-based inferences from the inherited adapter, not verified source methodology. They remain grouped as `legacy_date_inferred_*`. Modern history records display Rating 3.0. Matched provider records inherit only that observed displayed rating, with source attribution. Records without it use `no_rating_provided`.

The dashboard can show all maps for combat metrics. It suppresses a combined Rating mean or trend when multiple nonmissing rating groups are selected, and displays the number of rated observations. ADR excludes missing entries. `cs2_same_source_comparison.csv` compares G2 and Falcons using only the new provider's accepted maps, with metric sample counts; different dates and opponents prevent causal transfer-effect claims.

## Remaining gaps

- Sparse secondary coverage across 2021–2023; no completeness claim for those years.
- Late CS:GO after 2023-06-10 and early G2 CS2 before 2023-11-30.
- Additional provider omissions and quarantined observations; dates spanning a period do not establish all matches were captured.
- Historical opponent rankings, tournament stage, player role and weapon data.

`reports/coverage_calendar.csv` shows observed counts per month; zero means no loaded observations, not that the player did not compete.

## Rejected candidate

The Griffin DesRoches CS2 Kaggle dataset contains historical rows linked to scrape-time rosters/player averages (e.g. a 2024-05-15 Spirit row listing later players tn1r and zweih). It remains excluded from NiKo per-match statistics.

## Reproduction and licenses

`python -m tools.build_portfolio` rebuilds entirely offline from the checked-in canonical CSV. `python -m tools.integrate_cs2` regenerates the merge when the original public CS2 CSVs are available in `data/raw/source_audit/`; it uses the pre-integration baseline to avoid accumulating previous outputs. Raw datasets are excluded from publication archives.

See DATA_LICENSES.md for source-specific attribution, derivative licensing and the repository-declared MIT notice. No third-party data is relicensed as project code.
