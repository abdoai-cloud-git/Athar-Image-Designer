# Athar Image Designer Swarm - Deployment Guide

## 🚀 Complete Deployment Instructions

This guide provides step-by-step instructions for deploying the Athar Image Designer Swarm to production.

---

## ✅ Pre-Deployment Checklist

Before deploying, ensure you have:

- [ ] OpenAI API key
- [ ] KIE API key (for Nano Banana Pro)
- [ ] Google Cloud Project with Drive API enabled
- [ ] Google Service Account JSON credentials
- [ ] Google Drive folder ID
- [ ] GitHub account (for agencii.ai deployment)

---

## 📋 Step 1: Obtain API Keys

### 1.1 OpenAI API Key

1. Visit https://platform.openai.com/api-keys
2. Click "Create new secret key"
3. Name it: "Athar Image Designer Swarm"
4. Copy the key (starts with `sk-`)
5. Save securely - you'll need it for environment variables

**Cost**: GPT-5.1 pricing applies (~$10 per million tokens)

### 1.2 KIE API Key

1. Visit https://kie.ai
2. Sign up for an account
3. Navigate to Dashboard → API Keys
4. Click "Generate New API Key"
5. Copy the key
6. Save securely

**Note**: Verify Nano Banana Pro is available on your KIE plan

### 1.3 Google Service Account Setup

#### Create Google Cloud Project

1. Go to https://console.cloud.google.com/
2. Click "Select a project" → "New Project"
3. Name: "Athar Image Designer"
4. Click "Create"

#### Enable Google Drive API

1. In your project, go to "APIs & Services" → "Library"
2. Search for "Google Drive API"
3. Click "Enable"

#### Create Service Account

1. Go to "IAM & Admin" → "Service Accounts"
2. Click "Create Service Account"
3. Name: `athar-image-uploader`
4. Description: "Service account for Athar image uploads"
5. Click "Create and Continue"
6. Role: "Service Account User" (or skip role)
7. Click "Done"

#### Generate Service Account Key

1. Click on the service account you just created
2. Go to "Keys" tab
3. Click "Add Key" → "Create new key"
4. Select "JSON"
5. Click "Create"
6. Save the downloaded JSON file securely
7. **Important**: You'll need the entire JSON content as a single-line string

Example JSON structure:
```json
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "athar-image-uploader@your-project.iam.gserviceaccount.com",
  "client_id": "...",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "..."
}
```

### 1.4 Google Drive Folder Setup

1. Open Google Drive: https://drive.google.com
2. Create a new folder: "Athar Generated Images"
3. Right-click on the folder → "Share"
4. Add the service account email (from the JSON file: `client_email`)
   - Example: `athar-image-uploader@your-project.iam.gserviceaccount.com`
5. Set permission to **Editor**
6. Click "Send" (no notification needed)
7. Open the folder in Drive
8. Copy the folder ID from the URL:
   - URL format: `https://drive.google.com/drive/folders/[FOLDER_ID_HERE]`
   - Example: If URL is `https://drive.google.com/drive/folders/1aB2cD3eF4gH5iJ6kL7mN8oP9qR0sT1u`
   - Folder ID is: `1aB2cD3eF4gH5iJ6kL7mN8oP9qR0sT1u`

---

## 🌐 Step 2: Deploy to agencii.ai (Recommended)

### 2.1 Sign Up for Agencii

1. Visit https://agencii.ai
2. Click "Sign Up"
3. Create account or sign in with GitHub
4. Complete profile setup

### 2.2 Prepare Your Repository

1. **Push code to GitHub** (if not already done):
```bash
cd /workspace
git add .
git commit -m "Complete Athar Image Designer Swarm implementation"
git push origin main
```

2. **Verify repository contains**:
   - ✓ `agency.py`
   - ✓ `agencii.json`
   - ✓ `requirements.txt`
   - ✓ All agent folders
   - ✓ `.env.template` (NOT `.env` - never commit secrets!)

### 2.3 Connect Repository to Agencii

1. Go to Agencii Dashboard
2. Click "New Project" or "Connect Repository"
3. Click "Install Agencii GitHub App"
4. Select your repository
5. Grant required permissions
6. Return to Agencii Dashboard

### 2.4 Configure Environment Variables

In Agencii Dashboard:

1. Select your project
2. Go to "Settings" → "Environment Variables"
3. Add the following variables:

| Variable Name | Value | Example |
|--------------|-------|---------|
| `OPENAI_API_KEY` | Your OpenAI key | `sk-proj-...` |
| `KIE_API_KEY` | Your KIE API key | `kie_...` |
| `KIE_API_BASE` | KIE API base URL | `https://api.kie.ai/api/v1` |
| `GOOGLE_SERVICE_ACCOUNT_JSON` | Full JSON as single line | `{"type":"service_account",...}` |
| `GDRIVE_FOLDER_ID` | Google Drive folder ID | `1aB2cD3eF4gH5iJ...` |

**Important for `GOOGLE_SERVICE_ACCOUNT_JSON`**:
- Copy the ENTIRE JSON content from the downloaded file
- Format as a SINGLE LINE (remove all newlines within the JSON)
- Or use the raw JSON with escaped newlines in the private key

### 2.5 Deploy

1. In Agencii Dashboard, click "Deploy"
2. Select branch: `main`
3. Click "Deploy Now"
4. Wait for deployment to complete (2-5 minutes)
5. Monitor logs for any errors

### 2.6 Test Deployment

1. Once deployed, go to "Test" tab in Agencii
2. Enter test prompt:
   ```
   Create an image of a lone traveler walking through desert dunes at golden hour
   ```
3. Submit and monitor the workflow
4. Verify you receive:
   - ✓ Image URL from KIE
   - ✓ Google Drive view URL
   - ✓ Google Drive download URL
   - ✓ Generation seed

### 2.7 Production URL

After deployment, Agencii provides:
- **API Endpoint**: `https://your-agency.agencii.ai/api`
- **Web Interface**: `https://your-agency.agencii.ai`
- **Webhook URL**: `https://your-agency.agencii.ai/webhook`

---

## 💻 Step 3: Local Deployment (Development/Testing)

### 3.1 Setup Local Environment

1. **Clone repository** (if not already):
```bash
git clone <your-repo-url>
cd athar-image-designer-swarm
```

2. **Create virtual environment**:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

### 3.2 Configure Local Environment

1. **Copy environment template**:
```bash
cp .env.template .env
```

2. **Edit `.env` file** with your actual keys:
```bash
nano .env  # or use your preferred editor
```

Fill in:
```env
OPENAI_API_KEY=sk-proj-your-actual-key-here
KIE_API_KEY=your-kie-api-key-here
KIE_API_BASE=https://api.kie.ai/api/v1
GOOGLE_SERVICE_ACCOUNT_JSON={"type":"service_account","project_id":"..."}
GDRIVE_FOLDER_ID=your-folder-id-here
```

3. **Save and close**

### 3.3 Run Locally

**Terminal Mode** (Interactive):
```bash
python3 agency.py
```

Then interact with prompts like:
```
User: Create a minimalist image of solitude in nature
```

**Single Query Mode** (for testing):
```bash
python3 -c "
import asyncio
from agency import create_agency

async def test():
    agency = create_agency()
    response = await agency.get_response('Create an image of desert at sunset')
    print(response)

asyncio.run(test())
"
```

### 3.4 Verify Tools Work

Test each tool individually:

```bash
# Test Brief Extraction
python3 brief_agent/tools/ExtractBriefTool.py

# Test Prompt Generation
python3 art_direction_agent/tools/GeneratePromptTool.py

# Note: The following require API keys in .env
# Test KIE Image Generation (requires KIE_API_KEY)
# Test Validation (requires image URL)
# Test Google Drive Upload (requires all credentials)
```

---

## 🐳 Step 4: Docker Deployment (Self-Hosted)

### 4.1 Build Docker Image

```bash
docker build -t athar-image-designer-swarm .
```

### 4.2 Run Container

**With .env file**:
```bash
docker run -p 8000:8000 --env-file .env athar-image-designer-swarm
```

**With explicit environment variables**:
```bash
docker run -p 8000:8000 \
  -e OPENAI_API_KEY=sk-... \
  -e KIE_API_KEY=kie_... \
  -e KIE_API_BASE=https://api.kie.ai/api/v1 \
  -e GOOGLE_SERVICE_ACCOUNT_JSON='{"type":"service_account",...}' \
  -e GDRIVE_FOLDER_ID=1aB2cD3e... \
  athar-image-designer-swarm
```

### 4.3 Access Running Container

- API: http://localhost:8000
- Health Check: http://localhost:8000/health
- Logs: `docker logs -f <container-id>`

---

## 🔍 Step 5: Verification & Testing

### 5.1 Health Checks

**Agencii Dashboard**:
- Check "Status" page for green indicators
- Monitor "Logs" for any errors
- Verify all agents are listed

**Local/Docker**:
```bash
curl http://localhost:8000/health
```

### 5.2 End-to-End Test

Run a complete workflow test:

1. **Submit test prompt**:
   ```
   Create a cinematic image of a solitary figure in a vast desert landscape at golden hour. 
   The mood should be contemplative and serene, with warm earth tones and soft lighting.
   ```

2. **Expected workflow**:
   - ✓ Brief Agent extracts: theme, mood, palette
   - ✓ Art Direction Agent generates prompt
   - ✓ NB Image Agent creates image (1-3 minutes)
   - ✓ QA Agent validates quality
   - ✓ Export Agent uploads to Drive
   - ✓ Returns complete JSON response

3. **Expected output**:
   ```json
   {
     "theme": "solitude and contemplation",
     "prompt_used": "A cinematic minimalistic artwork...",
     "image_url": "https://...",
     "gdrive_url": "https://drive.google.com/file/d/.../view",
     "gdrive_download_url": "https://drive.google.com/uc?id=...&export=download",
     "seed": "12345",
     "aspect_ratio": "16:9",
     "filename": "athar_20241204_143022_seed_12345.png",
     "validation_status": "pass"
   }
   ```

### 5.3 Verify Google Drive

1. Open your Google Drive folder
2. Check that the image was uploaded
3. Verify filename format: `athar_YYYYMMDD_HHMMSS_seed_####.png`
4. Click on image to verify it opens
5. Test sharing URL works in incognito/private browser

---

## 🐛 Troubleshooting

### Common Issues

#### 1. "KIE_API_KEY not found"
**Solution**: Verify environment variable is set correctly
```bash
# Check if set
echo $KIE_API_KEY

# Or in Python
python3 -c "import os; print(os.getenv('KIE_API_KEY'))"
```

#### 2. "Insufficient permissions" (Google Drive)
**Solutions**:
- Verify service account email has Editor access to folder
- Check folder ID is correct
- Ensure Drive API is enabled in Google Cloud Console

#### 3. "Task creation failed" (KIE)
**Solutions**:
- Verify KIE API key is valid
- Check KIE account has access to Nano Banana Pro
- Verify API endpoint is correct: `https://api.kie.ai/api/v1`

#### 4. "Module not found"
**Solution**:
```bash
pip install -r requirements.txt
```

#### 5. Import Error for agency
**Solution**: Ensure you're in the project root directory
```bash
cd /workspace  # or your project root
python3 agency.py
```

---

## 📊 Monitoring & Maintenance

### Agencii Dashboard Monitoring

- **Metrics**: Track success rates, completion times
- **Logs**: Monitor for errors and warnings
- **Usage**: Track API costs (OpenAI, KIE)
- **Alerts**: Set up notifications for failures

### Cost Monitoring

**OpenAI**:
- GPT-5.1 usage per request
- Monitor at: https://platform.openai.com/usage

**KIE**:
- Nano Banana Pro generation costs
- Check KIE dashboard for usage

**Google Drive**:
- Storage costs (typically minimal)
- Monitor at: https://console.cloud.google.com/

---

## 🔐 Security Best Practices

1. **Never commit `.env` file** to Git
2. **Rotate API keys** regularly (every 90 days)
3. **Use least privilege** for service accounts
4. **Monitor access logs** in Agencii dashboard
5. **Set up alerts** for unusual activity
6. **Keep dependencies updated**:
   ```bash
   pip list --outdated
   pip install --upgrade agency-swarm
   ```

---

## 📈 Scaling Considerations

### Agencii Auto-Scaling

The `agencii.json` configuration includes:
- Min instances: 1
- Max instances: 5
- Auto-scale: true

Agencii automatically scales based on:
- Request volume
- Response times
- Queue length

### Performance Tuning

**For high volume**:
1. Increase `max_instances` in `agencii.json`
2. Consider caching common prompts
3. Batch requests when possible
4. Monitor and optimize slow agents

**For cost optimization**:
1. Reduce `max_instances`
2. Use smaller models for non-critical agents
3. Implement request throttling
4. Cache generated images

---

## 🎯 Next Steps

After successful deployment:

1. ✅ Test with various prompts
2. ✅ Monitor performance metrics
3. ✅ Set up regular cost reviews
4. ✅ Create backup/restore procedures
5. ✅ Document custom modifications
6. ✅ Train users on prompt best practices
7. ✅ Establish support channels

---

## 📞 Support

- **Agency Swarm**: https://agency-swarm.ai
- **Agencii Platform**: https://agencii.ai/support
- **KIE API**: https://kie.ai/docs
- **Project Issues**: GitHub Issues on your repository

---

**Congratulations!** Your Athar Image Designer Swarm is now deployed and ready to generate stunning cinematic images. 🎨✨
