# Quick Start - Testing Guide

This guide walks you through testing the Athar Image Designer Swarm step-by-step.

---

## Step 1: Environment Setup (5 minutes)

### 1.1 Create .env file
```bash
cp .env.template .env
```

### 1.2 Get API Keys

#### OpenAI API Key
1. Go to https://platform.openai.com/api-keys
2. Click "Create new secret key"
3. Copy key and add to `.env`:
   ```
   OPENAI_API_KEY=sk-proj-...
   ```

#### KIE API Key
1. Go to https://kie.ai
2. Sign up or log in
3. Navigate to API settings
4. Generate new API key
5. Add to `.env`:
   ```
   KIE_API_KEY=kie_...
   ```

#### Google Service Account (for Drive upload)
1. Go to https://console.cloud.google.com/
2. Create or select a project
3. Enable Google Drive API
4. Create Service Account:
   - IAM & Admin → Service Accounts → Create
   - Name: "athar-image-uploader"
   - Grant role: "Service Account User"
5. Create Key:
   - Click on service account
   - Keys → Add Key → Create New Key → JSON
   - Download JSON file
6. Copy entire JSON content to `.env` as single line:
   ```
   GOOGLE_SERVICE_ACCOUNT_JSON={"type":"service_account","project_id":"..."}
   ```

#### Google Drive Folder ID
1. Open Google Drive
2. Create folder: "Athar Generated Images"
3. Right-click → Share
4. Add service account email (from JSON: `client_email`)
5. Grant "Editor" permissions
6. Copy folder ID from URL:
   ```
   https://drive.google.com/drive/folders/[FOLDER_ID_HERE]
   ```
7. Add to `.env`:
   ```
   GDRIVE_FOLDER_ID=...
   ```

---

## Step 2: Run Tests (2 minutes)

### 2.1 Smoke Test
```bash
python3 test_workflow.py
```

**Expected Output**:
```
✓ PASS: Brief Tool JSON
✓ PASS: Art Direction Tool JSON
✓ PASS: KIE Endpoint
✓ PASS: Environment Variables
✨ ALL TESTS PASSED
```

### 2.2 Build Verification
```bash
python3 verify_build.py
```

**Expected Output**:
```
✓ Core files: PASS
✓ Agent structures: PASS
✓ Import test: PASS
✨ BUILD VERIFICATION: SUCCESS
```

---

## Step 3: Test Individual Tools (Optional, 3 minutes)

### 3.1 Test Brief Extraction
```bash
python3 brief_agent/tools/ExtractBriefTool.py
```

**Check**: Output should be pure JSON with `theme`, `mood`, `palette` fields

### 3.2 Test Art Direction
```bash
python3 art_direction_agent/tools/GeneratePromptTool.py
```

**Check**: Output should be pure JSON with `prompt`, `negative_prompt`, `aspect_ratio` fields

---

## Step 4: Local Agency Test (5-10 minutes)

### 4.1 Start Agency Terminal
```bash
python3 agency.py
```

### 4.2 Send Test Query
When terminal starts, enter:
```
Generate an Athar image about solitude and contemplation in the desert at sunset. Use aspect ratio 4:5.
```

### 4.3 Monitor Workflow

**Expected Flow**:
1. **Brief Agent** → Extracts JSON brief
2. **Art Direction Agent** → Generates JSON prompt
3. **NB Image Agent** → Creates KIE task, polls for completion (2-3 min)
4. **QA Agent** → Validates image
5. **Export Agent** → Uploads to Google Drive

### 4.4 Verify Results

You should receive:
- ✅ Image URL from KIE
- ✅ Google Drive view URL
- ✅ Google Drive download URL

Test the URLs in browser to confirm they work.

---

## Step 5: Production E2E Test (with actual content)

### 5.1 Using Canonical Athar Content

**Test Input** (if you have the PDF text):
```
اقترب من ذاتك أكثر
```

**Full Query**:
```
Generate an Athar image with text "اقترب من ذاتك أكثر", aspect ratio 4:5, cinematic-premium style
```

### 5.2 Expected Output

**Brief Agent Output** (JSON):
```json
{
  "theme": "...",
  "mood": "serene, contemplative",
  "palette": "warm earth tones, soft golden light",
  ...
}
```

**Art Direction Agent Output** (JSON):
```json
{
  "prompt": "A cinematic minimalistic artwork inspired by Athar...",
  "negative_prompt": "messy textures, chaotic shapes...",
  "aspect_ratio": "4:5",
  ...
}
```

**NB Image Agent Output** (JSON):
```json
{
  "success": true,
  "image_url": "https://...",
  "seed": "...",
  ...
}
```

**QA Agent Output** (JSON):
```json
{
  "approved": true,
  "status": "pass",
  ...
}
```

**Export Agent Output** (JSON):
```json
{
  "success": true,
  "gdrive_url": "https://drive.google.com/...",
  ...
}
```

---

## Troubleshooting

### If KIE Times Out

1. **Check API Key**:
   ```bash
   curl -H "Authorization: Bearer $KIE_API_KEY" \
        https://api.kie.ai/api/v1/playground/recordInfo?taskId=test
   ```
   Expected: JSON response (not 401/403)

2. **Check Network**:
   ```bash
   curl -I https://api.kie.ai
   ```
   Expected: HTTP 200

3. **Check Logs**:
   Look for:
   - "Task created successfully. Task ID: ..."
   - "Attempt X/60: Status = ..."

### If Agent Returns Non-JSON

**This should NOT happen**, but if it does:
1. Check which agent/tool
2. Run tool directly: `python3 path/to/tool.py`
3. Report output to developer

### If Drive Upload Fails

1. **Check Service Account JSON**:
   ```bash
   echo $GOOGLE_SERVICE_ACCOUNT_JSON | python3 -m json.tool
   ```
   Should parse without errors

2. **Check Folder Permissions**:
   - Open folder in Drive
   - Check that service account email has Editor access

3. **Check Folder ID**:
   ```bash
   echo $GDRIVE_FOLDER_ID
   ```
   Should be a long alphanumeric string

---

## Quick Validation Commands

### Check All Tools Return JSON
```bash
# Should output only JSON, no prose
python3 brief_agent/tools/ExtractBriefTool.py | python3 -m json.tool
python3 art_direction_agent/tools/GeneratePromptTool.py | python3 -m json.tool
```

### Validate .env Configuration
```bash
python3 -c "
from dotenv import load_dotenv
import os
load_dotenv()
print('OPENAI_API_KEY:', 'SET' if os.getenv('OPENAI_API_KEY') else 'NOT SET')
print('KIE_API_KEY:', 'SET' if os.getenv('KIE_API_KEY') else 'NOT SET')
print('GDRIVE_FOLDER_ID:', 'SET' if os.getenv('GDRIVE_FOLDER_ID') else 'NOT SET')
"
```

### Test KIE Endpoint
```bash
curl -I https://api.kie.ai/api/v1/playground/recordInfo
```
Expected: HTTP 200

---

## Success Criteria

✅ **All smoke tests pass**  
✅ **All tools return valid JSON**  
✅ **KIE API reachable**  
✅ **Agency runs without errors**  
✅ **Image URL accessible**  
✅ **Google Drive URL works**  
✅ **Total workflow time < 5 minutes**

---

## Next Steps After Testing

1. **If all tests pass**: Deploy to agencii.ai
2. **If any test fails**: Report exact error + logs
3. **For production**: Use same test query format

---

**Estimated Total Time**: 15-20 minutes  
**Difficulty**: Easy (copy-paste + API key setup)  
**Support**: See VERIFICATION_REPORT.md for detailed troubleshooting
