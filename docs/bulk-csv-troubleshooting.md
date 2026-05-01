# Bulk CSV Troubleshooting

This page covers common issues for:

- `pvw entity bulk-create-csv`
- `pvw entity bulk-update-csv`

## Quick Triage

1. Confirm CLI version and help options:

```bash
python -m purviewcli entity bulk-create-csv --help
python -m purviewcli entity bulk-update-csv --help
```

2. Run with an error output file:

```bash
python -m purviewcli entity bulk-update-csv \
  --csv-file .\\update.csv \
  --error-csv .\\failed_rows.csv
```

3. Start from Balanced profile and tune:

```bash
--batch-size 50 --throttle-ms 200 --max-retries 4 --retry-backoff-ms 1500 --retry-mode exponential
```

## Problem: Throttling (429 or intermittent API failures)

Symptoms:
- Requests fail in bursts
- Errors reduce when traffic slows down

Actions:
- Reduce `--batch-size` (for example 100 -> 50 -> 25)
- Increase `--throttle-ms` (for example 50 -> 200 -> 500)
- Use `--retry-mode exponential`
- Increase `--max-retries` for noisy environments

Safe baseline:

```bash
--batch-size 25 --throttle-ms 500 --max-retries 5 --retry-backoff-ms 2000 --retry-mode exponential
```

## Problem: Runtime is too slow

Symptoms:
- No errors, but processing time is too long

Actions:
- Increase `--batch-size` gradually
- Decrease `--throttle-ms` carefully
- Keep retries reasonable to avoid excessive rework loops

Fast baseline:

```bash
--batch-size 100 --throttle-ms 50 --max-retries 3 --retry-backoff-ms 1000 --retry-mode fixed
```

## Problem: CSV schema or mapping errors

Symptoms:
- Rows fail immediately
- Missing required fields errors
- Type mismatch or unknown field messages

Checks:
- For create, include `typeName` and `qualifiedName`
- For update, ensure GUID-driven rows are valid
- Verify header names match expected payload fields
- Use dot notation only for nested structures where supported

Useful pattern:
- Run with `--error-csv` and reprocess only failed rows after correction

## Problem: `pvw` help does not show new options

Cause:
- Installed console entry point may be stale compared to source code

Fix:

```bash
.\\.venv\\Scripts\\python.exe -m pip install -e .
```

Or run directly from source:

```bash
python -m purviewcli entity bulk-update-csv --help
```

## Recommended Defaults

Balanced profile is recommended for most tenants:

```bash
--batch-size 50 --throttle-ms 200 --max-retries 4 --retry-backoff-ms 1500 --retry-mode exponential
```

If throttling persists, move to Safe profile. If stable and too slow, move toward Fast profile.
