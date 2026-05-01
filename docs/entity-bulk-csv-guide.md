# Entity Bulk CSV Operations Guide

This page gives practical guidance for running bulk create and bulk update at good speed without triggering heavy throttling.

## Commands

```bash
# Bulk create from CSV
python -m purviewcli entity bulk-create-csv --csv-file .\\create.csv

# Bulk update from CSV
python -m purviewcli entity bulk-update-csv --csv-file .\\update.csv
```

Use `python -m purviewcli` to ensure you are running the latest source in this repo.

## Performance Options

Both commands support these options:

- `--batch-size`
- `--throttle-ms`
- `--max-retries`
- `--retry-backoff-ms`
- `--retry-mode` (`fixed` or `exponential`)

## Preset Profiles

### Fast

```bash
--batch-size 100 --throttle-ms 50 --max-retries 3 --retry-backoff-ms 1000 --retry-mode fixed
```

Use when API throttling is rare and you need max throughput.

### Balanced

```bash
--batch-size 50 --throttle-ms 200 --max-retries 4 --retry-backoff-ms 1500 --retry-mode exponential
```

Recommended default for most tenants.

### Safe

```bash
--batch-size 25 --throttle-ms 500 --max-retries 5 --retry-backoff-ms 2000 --retry-mode exponential
```

Use when your tenant is sensitive to burst traffic or you see frequent throttling.

## Practical Examples

### Balanced bulk create

```bash
python -m purviewcli entity bulk-create-csv \
  --csv-file .\\create.csv \
  --batch-size 50 \
  --throttle-ms 200 \
  --max-retries 4 \
  --retry-backoff-ms 1500 \
  --retry-mode exponential \
  --error-csv .\\create_failed.csv
```

### Balanced bulk update

```bash
python -m purviewcli entity bulk-update-csv \
  --csv-file .\\update.csv \
  --batch-size 50 \
  --throttle-ms 200 \
  --max-retries 4 \
  --retry-backoff-ms 1500 \
  --retry-mode exponential \
  --error-csv .\\update_failed.csv
```

## Tuning Rules

- If you get throttled often: lower `--batch-size` and increase `--throttle-ms`.
- If runs are stable and too slow: increase `--batch-size` or reduce `--throttle-ms`.
- Keep `--retry-mode exponential` for unstable environments.

## CSV Notes

- `bulk-create-csv` expects `typeName` and `qualifiedName`.
- `bulk-update-csv` supports GUID-driven rows and now uses bulk payload calls per batch.
- Use `--error-csv` to capture failed rows for reprocessing.
