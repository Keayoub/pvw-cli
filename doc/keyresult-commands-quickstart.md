# Key Results CLI Commands - Quick Start Guide

**Added:** November 5, 2025  
**Updated:** November 5, 2025  
**Feature:** OKR Key Results Management via CLI

---

## Overview

Key Results are measurable milestones that track progress toward Objectives (OKRs). Each Key Result has:
- **Definition:** Description of what you're measuring
- **Progress:** Current progress value
- **Goal:** Target value to achieve
- **Max:** Maximum possible value (for percentage calculations)
- **Status:** OnTrack, AtRisk, OffTrack, or Completed
- **Domain ID:** Governance domain the key result belongs to

---

## Available Commands

```bash
pvw uc keyresult list        # List all key results for an objective
pvw uc keyresult show         # Show details of a specific key result
pvw uc keyresult create       # Create a new key result
pvw uc keyresult update       # Update an existing key result
pvw uc keyresult delete       # Delete a key result
```

---

## Command Examples

### 1. List Key Results for an Objective

```bash
# List all key results
pvw uc keyresult list --objective-id <objective-guid>

# Output as JSON for scripting
pvw uc keyresult list --objective-id <objective-guid> --json
```

**Output:**
```
┏━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━┓
┃ ID           ┃ Name                    ┃ Target ┃ Current ┃ Status   ┃
┡━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━┩
│ abc-123...   │ Increase revenue        │ 100    │ 75      │ OnTrack  │
│ def-456...   │ Reduce customer churn   │ 5      │ 7       │ AtRisk   │
└──────────────┴─────────────────────────┴────────┴─────────┴──────────┘
```

---

### 2. Create a Key Result

```bash
# Create a data quality key result
pvw uc keyresult create \
  --objective-id <objective-guid> \
  --governance-domain-id <domain-guid> \
  --definition "Reduce data validation errors in financial reports" \
  --progress 5 \
  --goal 25 \
  --max 100 \
  --status "OnTrack"

# Create a lineage documentation key result
pvw uc keyresult create \
  --objective-id <objective-guid> \
  --governance-domain-id <domain-guid> \
  --definition "Complete data lineage documentation for top 50 critical datasets" \
  --progress 12 \
  --goal 50 \
  --max 50 \
  --status "OnTrack"

# Create with minimal options (defaults: progress=0, max=100, status=OnTrack)
pvw uc keyresult create \
  --objective-id <objective-guid> \
  --governance-domain-id <domain-guid> \
  --definition "Implement automated data quality checks" \
  --goal 10
```

**Parameters:**
- `--objective-id` (required): Parent objective GUID
- `--governance-domain-id` (required): Governance domain GUID
- `--definition` (required): Description of what you're measuring
- `--goal` (required): Target value to achieve
- `--progress` (optional): Current progress value (default: 0)
- `--max` (optional): Maximum possible value (default: 100)
- `--status` (optional): OnTrack, AtRisk, OffTrack, or Completed (default: OnTrack)

---

### 3. Show Key Result Details

```bash
# View full details in JSON format
pvw uc keyresult show \
  --objective-id <objective-guid> \
  --key-result-id <key-result-guid>
```

**Output:**
```json
{
  "id": "abc-123-...",
  "name": "Increase quarterly revenue",
  "targetValue": 1000000,
  "currentValue": 750000,
  "unit": "$",
  "status": "OnTrack",
  "description": "Target: $1M in Q4 revenue",
  "progress": 75.0,
  "createdBy": "user@company.com",
  "createdAt": "2025-11-01T10:00:00Z",
  "updatedAt": "2025-11-05T14:30:00Z"
}
```

---

### 4. Update a Key Result

> **⚠️ Important:** The update command uses HTTP PUT, which requires ALL fields to be provided. 
> If you omit optional fields, they will be cleared. Always include all fields you want to keep.

```bash
# Update progress value
pvw uc keyresult update \
  --objective-id <objective-guid> \
  --key-result-id <key-result-guid> \
  --governance-domain-id <domain-guid> \
  --definition "Reduce data validation errors in financial reports" \
  --progress 15 \
  --goal 25 \
  --status "OnTrack"

# Update status to at risk
pvw uc keyresult update \
  --objective-id <objective-guid> \
  --key-result-id <key-result-guid> \
  --governance-domain-id <domain-guid> \
  --definition "Complete data lineage documentation for top 50 critical datasets" \
  --progress 18 \
  --goal 50 \
  --max 50 \
  --status "AtRisk"

# Mark as completed
pvw uc keyresult update \
  --objective-id <objective-guid> \
  --key-result-id <key-result-guid> \
  --governance-domain-id <domain-guid> \
  --definition "Implement automated data quality checks" \
  --progress 10 \
  --goal 10 \
  --max 10 \
  --status "Completed"
```

**Parameters:**
- `--objective-id` (required): Parent objective GUID
- `--key-result-id` (required): Key result GUID to update
- `--governance-domain-id` (optional): Governance domain GUID
- `--definition` (optional): New definition text
- `--progress` (optional): New progress value
- `--goal` (optional): New goal value
- `--max` (optional): New maximum value
- `--status` (optional): New status (OnTrack, AtRisk, OffTrack, Completed)

> **⚠️ Note:** If you don't provide optional fields, they may be cleared due to PUT behavior

---

### 5. Delete a Key Result

```bash
# Delete with confirmation prompt
pvw uc keyresult delete \
  --objective-id <objective-guid> \
  --key-result-id <key-result-guid>

# Delete without confirmation (use with caution!)
pvw uc keyresult delete \
  --objective-id <objective-guid> \
  --key-result-id <key-result-guid> \
  --yes
```

---

## Complete OKR Workflow Example

Here's a complete workflow for managing OKRs (Objectives and Key Results):

```bash
# 1. Create an objective
pvw uc objective create \
  --definition "Improve customer satisfaction and retention" \
  --domain-id <domain-guid> \
  --status "Draft" \
  --target-date "2025-12-31T23:59:59.000Z"

# Output: Get objective ID from response
OBJECTIVE_ID="abc-123-456-..."

# 2. Create key results for the objective
pvw uc keyresult create \
  --objective-id $OBJECTIVE_ID \
  --name "Increase NPS score" \
  --target-value 80 \
  --current-value 65 \
  --unit "points" \
  --status "OnTrack"

pvw uc keyresult create \
  --objective-id $OBJECTIVE_ID \
  --name "Reduce customer churn rate" \
  --target-value 5 \
  --current-value 8 \
  --unit "%" \
  --status "AtRisk"

pvw uc keyresult create \
  --objective-id $OBJECTIVE_ID \
  --name "Complete customer onboarding improvements" \
  --target-value 100 \
  --current-value 40 \
  --unit "%" \
  --status "OnTrack"

# 3. View all key results
pvw uc keyresult list --objective-id $OBJECTIVE_ID

# 4. Update progress regularly
pvw uc keyresult update \
  --objective-id $OBJECTIVE_ID \
  --key-result-id <key-result-1-guid> \
  --current-value 70

pvw uc keyresult update \
  --objective-id $OBJECTIVE_ID \
  --key-result-id <key-result-2-guid> \
  --current-value 6.5 \
  --status "OnTrack"

# 5. Mark completed key results
pvw uc keyresult update \
  --objective-id $OBJECTIVE_ID \
  --key-result-id <key-result-3-guid> \
  --current-value 100 \
  --status "Completed"
```

---

## PowerShell Scripting Examples

### Bulk Progress Update

```powershell
# Update progress for multiple key results
$objectiveId = "abc-123-..."
$updates = @(
    @{ id = "kr-001"; value = 75 },
    @{ id = "kr-002"; value = 82 },
    @{ id = "kr-003"; value = 100 }
)

foreach ($update in $updates) {
    py -m purviewcli uc keyresult update `
        --objective-id $objectiveId `
        --key-result-id $update.id `
        --current-value $update.value
    
    Write-Host "Updated key result $($update.id) to $($update.value)%" -ForegroundColor Green
    Start-Sleep -Milliseconds 200  # Rate limiting
}
```

### Generate Progress Report

```powershell
# Get all key results and calculate overall objective progress
$objectiveId = "abc-123-..."
$keyResults = py -m purviewcli uc keyresult list --objective-id $objectiveId --json | ConvertFrom-Json

$totalProgress = 0
$count = $keyResults.Count

foreach ($kr in $keyResults) {
    $progress = ($kr.currentValue / $kr.targetValue) * 100
    $totalProgress += $progress
    
    Write-Host "$($kr.name): $($progress.ToString('0.0'))% ($($kr.currentValue)/$($kr.targetValue) $($kr.unit))" -ForegroundColor Cyan
}

$avgProgress = $totalProgress / $count
Write-Host "`nOverall Objective Progress: $($avgProgress.ToString('0.0'))%" -ForegroundColor Yellow
```

### Status Dashboard

```powershell
# Create a status dashboard for all key results
$objectiveId = "abc-123-..."
$keyResults = py -m purviewcli uc keyresult list --objective-id $objectiveId --json | ConvertFrom-Json

Write-Host "`n=== Key Results Status Dashboard ===" -ForegroundColor Cyan

$onTrack = @($keyResults | Where-Object { $_.status -eq "OnTrack" }).Count
$atRisk = @($keyResults | Where-Object { $_.status -eq "AtRisk" }).Count
$offTrack = @($keyResults | Where-Object { $_.status -eq "OffTrack" }).Count
$completed = @($keyResults | Where-Object { $_.status -eq "Completed" }).Count

Write-Host "  On Track: $onTrack" -ForegroundColor Green
Write-Host "  At Risk: $atRisk" -ForegroundColor Yellow
Write-Host "  Off Track: $offTrack" -ForegroundColor Red
Write-Host "  Completed: $completed" -ForegroundColor Blue

if ($atRisk -gt 0 -or $offTrack -gt 0) {
    Write-Host "`nKey Results Needing Attention:" -ForegroundColor Yellow
    $keyResults | Where-Object { $_.status -in @("AtRisk", "OffTrack") } | ForEach-Object {
        Write-Host "  - $($_.name) [$($_.status)]" -ForegroundColor Red
    }
}
```

---

## Status Values

| Status | Description | When to Use |
|--------|-------------|-------------|
| `OnTrack` | Progressing as expected | Current value is meeting or exceeding pace to hit target |
| `AtRisk` | Behind pace but recoverable | Current value is below expected pace but target still achievable |
| `OffTrack` | Significantly behind | Current value makes target unlikely without major changes |
| `Completed` | Target achieved | Current value meets or exceeds target value |

---

## Tips & Best Practices

1. **Set SMART Key Results:**
   - Specific: Clear and unambiguous
   - Measurable: Has a target value and unit
   - Achievable: Realistic given resources
   - Relevant: Directly supports the objective
   - Time-bound: Associated with objective timeline

2. **Update Regularly:**
   - Update current values weekly or bi-weekly
   - Adjust status as progress changes
   - Document significant changes in description

3. **Use Appropriate Units:**
   - Percentages: `%`
   - Currency: `$`, `€`, `£`
   - Counts: `users`, `items`, `tickets`
   - Scores: `points`, `rating`

4. **Limit Key Results per Objective:**
   - Recommended: 3-5 key results per objective
   - Too many dilutes focus
   - Too few may not capture full objective

5. **Review and Cleanup:**
   - Archive completed objectives and key results
   - Delete draft key results that are no longer relevant
   - Keep historical data for trend analysis

---

## Troubleshooting

### Common Issues

**Issue:** "Key result not found"
- **Solution:** Verify both objective-id and key-result-id are correct GUIDs

**Issue:** "Objective not found"
- **Solution:** Check that the objective exists: `pvw uc objective show --objective-id <guid>`

**Issue:** "Invalid target value"
- **Solution:** Target value must be a number (integer or decimal)

**Issue:** "Current value exceeds target"
- **Solution:** This is allowed! It means you exceeded your goal. Update status to "Completed"

---

## Related Commands

- **Objectives:** `pvw uc objective list/create/show/update/delete/query`
- **Domains:** `pvw uc domain list/create/show`
- **Help:** `pvw uc keyresult --help`

---

## API Endpoints Used

| Command | HTTP Method | Endpoint |
|---------|-------------|----------|
| list | GET | `/datagovernance/catalog/objectives/{objectiveId}/keyResults` |
| show | GET | `/datagovernance/catalog/objectives/{objectiveId}/keyResults/{keyResultId}` |
| create | POST | `/datagovernance/catalog/objectives/{objectiveId}/keyResults` |
| update | PATCH | `/datagovernance/catalog/objectives/{objectiveId}/keyResults/{keyResultId}` |
| delete | DELETE | `/datagovernance/catalog/objectives/{objectiveId}/keyResults/{keyResultId}` |

---

## Next Steps

1. **Create your first objective:**
   ```bash
   pvw uc objective create --definition "Your objective" --domain-id <guid>
   ```

2. **Add key results:**
   ```bash
   pvw uc keyresult create --objective-id <guid> --name "KR1" --target-value 100
   ```

3. **Track progress:**
   ```bash
   pvw uc keyresult list --objective-id <guid>
   ```

For more information, see:
- [OKR Best Practices](https://learn.microsoft.com/purview/unified-catalog)
- [Data Governance Guide](../data-governance-api-gap-analysis.md)
