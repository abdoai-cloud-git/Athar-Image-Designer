# Athar Image Designer Swarm

A production-ready multi-agent system for generating high-quality cinematic Athar-style images using **Nano Banana Pro** via the **KIE API**.

## 🎨 Overview

The Athar Image Designer Swarm is a sophisticated AI agent system that transforms user descriptions into stunning, cinematic images that embody Athar's distinctive aesthetic: minimalist compositions, contemplative themes, warm earth tones, and poetic atmosphere.

### Key Features

- ✨ **Athar-Optimized**: Specifically designed for Athar's cinematic, minimalist aesthetic
- 🤖 **Multi-Agent Architecture**: 5 specialized agents working in seamless coordination
- 🎯 **KIE API Integration**: Direct integration with Nano Banana Pro through KIE API
- ☁️ **Cloud Storage**: Automatic upload to Google Drive with shareable URLs
- ✅ **Quality Assurance**: Automated validation for aspect ratio, clarity, and quality
- 🚀 **Production Ready**: Deploy directly to agencii.ai dashboard

## 🏗️ Architecture

```
User Input
    ↓
Brief Agent → Extracts creative brief (theme, mood, palette)
    ↓
Art Direction Agent → Generates optimized Nano Banana prompt
    ↓
NB Image Agent → Generates image via KIE API
    ↓
QA Agent → Validates quality (retry if needed)
    ↓
Export Agent → Uploads to Google Drive
    ↓
Returns URLs and metadata to user
```

### Agents

1. **Brief Agent** - Extracts creative elements from user input
2. **Art Direction Agent** - Converts brief into optimized prompts
3. **NB Image Agent** - Generates images via Nano Banana Pro (KIE API)
4. **QA Agent** - Validates image quality and technical specs
5. **Export Agent** - Uploads to Google Drive and returns URLs

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- OpenAI API key
- KIE API key (for Nano Banana Pro access)
- Google Service Account with Drive API access

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd athar-image-designer-swarm
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment variables**

Copy `.env.template` to `.env` and fill in your API keys:

```bash
cp .env.template .env
# Edit .env with your API keys
```

Required environment variables:
- `OPENAI_API_KEY` - Your OpenAI API key
- `KIE_API_KEY` - Your KIE API key for Nano Banana Pro
- `GOOGLE_SERVICE_ACCOUNT_JSON` - Google Service Account credentials (JSON)
- `GDRIVE_FOLDER_ID` - Google Drive folder ID for uploads

### Running Locally

```bash
python agency.py
```

This launches the agency in terminal mode where you can test image generation.

### Example Usage

```
User: Create an image of solitude in the desert at sunset. 
      A lone figure contemplates the vast expanse, bathed in golden light. 
      Mood: peaceful and meditative, warm earth tones.

Agency:
  ↓ Brief Agent extracts: theme=solitude, mood=serene, palette=warm earth tones
  ↓ Art Direction Agent creates optimized prompt
  ↓ NB Image Agent generates via KIE API
  ↓ QA Agent validates quality → PASS
  ↓ Export Agent uploads to Google Drive
  
Returns:
  - Image URL (KIE)
  - Google Drive View URL
  - Google Drive Download URL
  - Generation seed (for reproducibility)
  - Complete metadata
```

## 🔧 Setup Instructions

### 1. OpenAI API Key

1. Visit https://platform.openai.com/api-keys
2. Create new secret key
3. Add to `.env` as `OPENAI_API_KEY`

### 2. KIE API Key

1. Visit https://kie.ai
2. Sign up or log in
3. Navigate to API settings
4. Generate new API key
5. Add to `.env` as `KIE_API_KEY`

### 3. Google Service Account

1. Go to https://console.cloud.google.com/
2. Create or select a project
3. Enable Google Drive API
4. Create Service Account:
   - IAM & Admin → Service Accounts → Create Service Account
   - Name it (e.g., "athar-image-uploader")
   - Grant role: "Service Account User"
5. Create Key:
   - Click on service account
   - Keys → Add Key → Create New Key → JSON
   - Download JSON file
   - Copy entire JSON content to `.env` as single-line string

### 4. Google Drive Folder

1. Open Google Drive
2. Create new folder (e.g., "Athar Generated Images")
3. Right-click → Share
4. Add your service account email (from JSON: `client_email`)
5. Give **Editor** permissions
6. Copy folder ID from URL: `https://drive.google.com/drive/folders/[FOLDER_ID]`
7. Add to `.env` as `GDRIVE_FOLDER_ID`

## 📁 Project Structure

```
athar-image-designer-swarm/
├── brief_agent/
│   ├── brief_agent.py
│   ├── instructions.md
│   └── tools/
│       └── ExtractBriefTool.py
├── art_direction_agent/
│   ├── art_direction_agent.py
│   ├── instructions.md
│   └── tools/
│       └── GeneratePromptTool.py
├── nb_image_agent/
│   ├── nb_image_agent.py
│   ├── instructions.md
│   └── tools/
│       └── KieNanoBananaTool.py
├── qa_agent/
│   ├── qa_agent.py
│   ├── instructions.md
│   └── tools/
│       └── ValidateImageTool.py
├── export_agent/
│   ├── export_agent.py
│   ├── instructions.md
│   └── tools/
│       └── GDriveUploadTool.py
├── agency.py                    # Main agency orchestration
├── shared_instructions.md       # Shared context for all agents
├── agencii.json                 # Deployment configuration
├── deployment.sh                # Deployment script
├── requirements.txt             # Python dependencies
├── .env.template                # Environment variable template
└── README.md                    # This file
```

## 🌐 Deployment to agencii.ai

### Automated Deployment

1. **Push to GitHub**
```bash
git add .
git commit -m "Initial Athar Image Designer Swarm setup"
git push origin main
```

2. **Connect to agencii.ai**
   - Sign up at https://agencii.ai
   - Install the [Agencii GitHub App](https://github.com/apps/agencii)
   - Grant permissions to your repository

3. **Configure Environment Variables**
   - Go to agencii.ai dashboard
   - Add all required environment variables:
     - `OPENAI_API_KEY`
     - `KIE_API_KEY`
     - `GOOGLE_SERVICE_ACCOUNT_JSON`
     - `GDRIVE_FOLDER_ID`

4. **Deploy**
   - Agencii automatically deploys on push to `main` branch
   - Monitor deployment in dashboard
   - Access your live agency via provided endpoints

### Manual Deployment

```bash
./deployment.sh
```

The deployment script will:
- Verify environment configuration
- Install dependencies
- Validate agency structure
- Test imports
- Provide deployment options

## 🔍 Testing

### Test Individual Tools

```bash
# Test Brief Extraction
python brief_agent/tools/ExtractBriefTool.py

# Test Prompt Generation
python art_direction_agent/tools/GeneratePromptTool.py

# Test Image Generation (requires KIE_API_KEY)
python nb_image_agent/tools/KieNanoBananaTool.py

# Test Image Validation (requires image URL)
python qa_agent/tools/ValidateImageTool.py

# Test Google Drive Upload (requires all credentials)
python export_agent/tools/GDriveUploadTool.py
```

### Test Complete Agency

```bash
python agency.py
```

Then enter a test prompt like:
```
Create an image of a lone traveler in the desert at golden hour
```

## 📊 Workflow Details

### Sequential Pipeline

1. **Brief Agent** receives user input
   - Extracts theme, mood, tone, palette, visual elements, keywords
   - Outputs structured JSON brief

2. **Art Direction Agent** receives brief
   - Applies Athar prompt template
   - Generates main prompt and negative prompt
   - Adds technical parameters (aspect ratio, style)

3. **NB Image Agent** receives prompt
   - Creates task via KIE API: `POST /playground/createTask`
   - Polls status via: `GET /playground/recordInfo?taskId=xxx`
   - Waits for "completed" status
   - Returns image URL(s) and metadata

4. **QA Agent** receives image URL
   - Downloads and validates image
   - Checks: aspect ratio, resolution, quality, exposure, color
   - Decides: PASS / PASS_WITH_WARNINGS / RETRY

5. **Export Agent** receives validated image (if PASS)
   - Downloads from KIE URL
   - Uploads to Google Drive
   - Makes publicly accessible
   - Returns view and download URLs

### Retry Logic

If QA Agent returns RETRY:
- Image is rejected with specific issues noted
- Request loops back to NB Image Agent
- Agent can adjust parameters and regenerate
- Max retries: 2 (configurable in `agencii.json`)

## 🎨 Athar Style Guidelines

### Visual Characteristics

- **Composition**: Rule of thirds, generous negative space, single focal point
- **Lighting**: Soft, directional, warm golden hour or blue hour
- **Texture**: Paper grain, subtle film grain, organic textures
- **Color**: Warm earth tones, muted pastels, controlled saturation
- **Mood**: Calm, contemplative, meditative, introspective, poetic

### Common Themes

- Solitude and contemplation
- Journey and exploration  
- Spirituality and transcendence
- Memory and nostalgia
- Silence and stillness
- Nature and landscape

### What to Avoid

- Harsh lighting
- Oversaturation
- Busy compositions
- Multiple focal points
- Chaotic textures
- Distorted text

## 🔧 Configuration

### agencii.json

Deployment configuration for agencii.ai platform:
- Agent definitions and roles
- Workflow type (sequential_pipeline)
- Environment variable requirements
- Scaling settings
- Health checks
- Performance expectations

### shared_instructions.md

Shared context for all agents:
- Athar brand background
- Style guidelines
- Quality standards
- Technical specifications
- Workflow coordination

## 📈 Performance Metrics

- **Expected Completion Time**: 2-5 minutes
- **Generation Success Rate**: >95%
- **QA Pass Rate**: >80% on first attempt
- **Upload Success Rate**: >99%
- **Timeout Threshold**: 10 minutes

## 🛠️ Troubleshooting

### Common Issues

**Import Error: `ModuleNotFoundError`**
```bash
pip install -r requirements.txt
```

**KIE API Error: `Unauthorized`**
- Check `KIE_API_KEY` is set correctly in `.env`
- Verify API key is active at https://kie.ai

**Google Drive Error: `Insufficient permissions`**
- Verify service account email has Editor access to folder
- Check `GOOGLE_SERVICE_ACCOUNT_JSON` is valid JSON
- Ensure Drive API is enabled in Google Cloud Console

**Image Generation Timeout**
- Default timeout: 60 polling attempts × 5 seconds = 5 minutes
- Check KIE API status
- Verify image generation is not stuck in "processing"

### Debug Mode

For verbose logging:
```bash
export LOG_LEVEL=DEBUG
python agency.py
```

## 📚 Documentation

- [Agency Swarm Documentation](https://agency-swarm.ai)
- [KIE API Documentation](https://kie.ai/docs)
- [Google Drive API Guide](https://developers.google.com/drive/api/guides/about-sdk)
- [Agencii Platform](https://agencii.ai)

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- **Agency Swarm** - Multi-agent orchestration framework
- **KIE AI** - Nano Banana Pro API access
- **OpenAI** - GPT-5.1 model for agent reasoning
- **Athar** - Inspiration for aesthetic guidelines

---

**Ready to generate stunning Athar-style images?** 🎨✨

For support or questions, please open an issue or visit our documentation.
