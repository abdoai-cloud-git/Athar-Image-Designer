# Bug Fix Summary: JSON Error Format for Agent Communication

## Issue Description
The PR modified `_format_result` to return pure JSON for successful cases, but error paths in `run()` methods still returned plain string messages. This broke agent-to-agent communication when downstream agents expected JSON.

## Root Cause
- `KieNanoBananaTool.run()` lines 58-71: Returned plain strings like `"Error: KIE_API_KEY not found..."`
- `GDriveUploadTool.run()` lines 47-64: Returned plain strings like `"Error: GOOGLE_SERVICE_ACCOUNT_JSON not found..."`
- Only `ValidateImageTool` correctly used `_format_result()` for all error paths

## Solution

### 1. Updated `KieNanoBananaTool` (/workspace/nb_image_agent/tools/KieNanoBananaTool.py)

**Modified `_format_result()` method** (lines 171-202):
- Added `error` parameter to handle error cases
- Returns JSON for all error conditions: `{"success": false, "error": "message"}`

**Updated `run()` method** (lines 58-71):
- Changed 4 error return statements from plain strings to `_format_result(None, error="message")`
- Error cases now handled:
  1. Missing KIE_API_KEY
  2. Failed to create task
  3. Task failed or timed out
  4. No task data available

**Before:**
```python
if not KIE_API_KEY:
    return "Error: KIE_API_KEY not found..."
```

**After:**
```python
if not KIE_API_KEY:
    return self._format_result(None, error="KIE_API_KEY not found...")
```

### 2. Updated `GDriveUploadTool` (/workspace/export_agent/tools/GDriveUploadTool.py)

**Modified `_format_result()` method** (lines 202-224):
- Added `error` parameter to handle error cases
- Returns JSON for all error conditions: `{"success": false, "error": "message"}`

**Updated `run()` method** (lines 47-64):
- Changed 4 error return statements from plain strings to `_format_result(None, error="message")`
- Error cases now handled:
  1. Missing GOOGLE_SERVICE_ACCOUNT_JSON
  2. Missing folder_id
  3. Failed to download image
  4. Failed to upload to Google Drive

**Before:**
```python
if not GOOGLE_SERVICE_ACCOUNT_JSON:
    return "Error: GOOGLE_SERVICE_ACCOUNT_JSON not found..."
```

**After:**
```python
if not GOOGLE_SERVICE_ACCOUNT_JSON:
    return self._format_result(None, error="GOOGLE_SERVICE_ACCOUNT_JSON not found...")
```

## Verification

All error paths now return valid JSON format:

```json
{
  "success": false,
  "error": "Descriptive error message"
}
```

This ensures:
- ✅ Downstream agents can parse responses consistently
- ✅ Error handling is uniform across all tools
- ✅ Agent-to-agent communication works reliably
- ✅ Matches the pattern established by `ValidateImageTool`

## Impact

**Files Modified:**
1. `/workspace/nb_image_agent/tools/KieNanoBananaTool.py`
2. `/workspace/export_agent/tools/GDriveUploadTool.py`

**Breaking Changes:** None - Error returns now follow the same JSON format as success cases

**Testing:** All error paths validated to return parseable JSON with `success: false` and `error` message fields.
