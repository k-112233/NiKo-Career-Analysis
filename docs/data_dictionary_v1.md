# v1 data dictionary

Grain: one accepted NiKo **map observation**, not one series. Canonical input: `data/processed/niko_maps.csv`.

| Fields | Meaning |
|---|---|
| `record_id` | Unique project key, with source namespace; a hash key is not an official HLTV ID |
| `date`, `source_datetime` | Source-reported match date and optional timestamp; no inferred local-time conversion |
| `team`, `opponent`, `map` | Career team, opponent and played map |
| `kills`, `deaths`, `assists` | Map combat counts; blank means unavailable |
| `adr` | Source average damage per round; blank means unavailable |
| `kast` | Source KAST percentage on a 0–100 scale |
| `rating`, `rating_group`, `rating_version` | Observed rating and methodology label; legacy version labels are date inferences, provider-only maps have no rating |
| `team_score`, `opponent_score`, `result` | Map scores where supplied; win/loss/draw relative to NiKo's team |
| `event_id`, `event_name`, `year` | Source/derived tournament metadata; `Unknown` is not a tournament classification |
| `source`, `source_url`, `collected_date` | Source layer, provenance link and snapshot acquisition date |
| `player_id`, `player_link` | HLTV identity where supplied; not populated with another provider's ID |
| `provider_player_id`, `provider_map_id`, `series_id` | Provider-specific identifiers; not interchangeable with HLTV IDs |
| `identity_method`, `identity_confidence` | Identity audit method and evidence label, not a numerical probability |
| `rating_source` | Independent history-page source for successfully matched Rating observations |
| `data_license`, `coverage_note` | Layer-specific license label and coverage context |

K/D = total kills / total deaths over maps with both counts; zero total deaths yields missing. Rating and ADR are map-equal means over available observations, accompanied by valid counts. Rating means are suppressed when multiple nonmissing methodology groups are pooled. Win rate excludes draw/unknown. Wilson intervals are descriptive; maps from a series are correlated and not independent trials. CSV blanks and JSON nulls represent missing values, never zero performance.

`reports/manifest.json` records the canonical CSV SHA-256. `reports/cs2_reconciliation.csv` preserves accepted, quarantined and unmatched joins. `reports/coverage_calendar.csv` counts observations, not all matches played.
