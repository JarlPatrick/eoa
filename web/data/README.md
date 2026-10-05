# Contest status and files

`result-metadata.json` is keyed by the internal subcontest ID. Optional `status` values are `complete`, `partial`, and `source-only`. `questions`, `regulations`, and `source` can each contain a `sourceUrl` (original reference) and a `localUrl` (a file served from `web/public/`). Keep both when a local copy exists.

`competition-occurrences.json` records facts for a year, contest type, and age group with no result row in the database. Its key is the JSON encoding of `[subject code, contest type, age group, academic start year]`. Use `status: "not-held"` only when a source confirms the competition did not happen. Use `status: "source-only"` when an original source exists but results have not been entered. All missing keys are shown as unknown (`?`).

These files are a bridge until the database stores occurrence status and source documents directly. Avoid marking results complete or a competition absent based only on missing database rows.
