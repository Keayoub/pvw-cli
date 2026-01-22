# Test Results: Custom Attributes with Different Data Types

## Overview
Successfully tested creating custom attribute definitions with different data types and using them in business terms via CSV import.

## Part 1: Custom Attribute Definition Creation

### Tested Data Types:
✅ **String** - `TestAttributeString` - Text values
✅ **Number** - `TestAttributeNumber` - Numeric values (integer/decimal)
✅ **Boolean** - `TestAttributeBoolean` - True/false values
✅ **Date** - `TestAttributeDate` - ISO 8601 date format

All 4 custom attribute definitions were created successfully via CLI commands:
```bash
.venv\Scripts\python.exe -m purviewcli uc attribute create \
  --name "TestAttributeString" \
  --data-type "string" \
  --description "Test string attribute"
```

## Part 2: Using Custom Attributes with Terms (Managed Attributes)

Custom attributes (as managedAttributes) were successfully created on terms with various types:

### JSON List Type Example:
```json
{
  "name": "Glossaire.SecteursActivite",
  "value": "[\"Banque\", \"Assurance\", \"Finance\"]"
}
```

### CSV Import Format:
```csv
name,description,status,customAttributes.Glossaire.SecteursActivite
TEST-debug-01,Terme de test avec liste de secteurs,Draft,"[""Banque"",""Assurance"",""Finance""]"
TEST-debug-02,Terme avec secteurs IT,Draft,"[""Cloud"",""Data"",""Infrastructure""]"
```

### Successfully Created Terms:
- **TEST-debug-01**: Custom attribute with JSON list of sectors
- **TEST-debug-02**: Custom attribute with JSON list of IT domains

## Part 3: Data Type Support in Managed Attributes

The following value types are supported when storing managed attributes:

✅ **String Values**
- Simple text: `"value": "Finance"`
- JSON Strings: `"value": "[\"Bank\", \"Insurance\"]"` (for arrays)

✅ **Number Values** (as strings in JSON)
- Integers: `"value": "42"`
- Decimals: `"value": "3.14"`

✅ **Boolean Values** (as strings in JSON)
- True/False: `"value": "true"` or `"value": "false"`

✅ **Date Values** (as ISO 8601 strings)
- Dates: `"value": "2026-01-22"`
- DateTime: `"value": "2026-01-22T16:13:21.190Z"`

✅ **Complex Types** (as JSON strings)
- Arrays: `"value": "[1, 2, 3]"` or `"value": "[\"item1\", \"item2\"]"`
- Objects: `"value": "{\"key\": \"value\"}"`

## Part 4: Whitespace Handling

✅ **Automatic .strip() Applied**
All string parameters now automatically remove leading/trailing whitespace:
- Input: `"  TEST-STRIP-SPACES  "` → Output: `"TEST-STRIP-SPACES"`
- Input: `"  Test term with spaces  "` → Output: `"Test term with spaces"`

## Conclusion

✅ Custom attribute definitions support 4 data types: string, number, boolean, date
✅ Custom attributes can be applied to terms via CSV import
✅ Complex data types (lists, objects) are supported as JSON-serialized strings
✅ Whitespace is automatically stripped from all string inputs
✅ Terms with custom attributes display correctly via list command with --show-attributes flag

## Test Files Generated
- `test_custom_attributes.ps1` - PowerShell test script
- `test_import_list.csv` - CSV with list-valued custom attributes
