# Athar Image Designer Swarm

A production-ready multi-agent system for generating high-quality cinematic Athar-style images using Nano Banana Pro via the KIE API.

## Overview

This Agency Swarm system orchestrates a sequential workflow to transform user input into production-ready Athar-style images:

1. **Brief Agent** - Extracts theme, tone, palette, and keywords
2. **Art Direction Agent** - Converts briefs into complete Nano Banana prompts
3. **NB Image Agent** - Generates images via KIE API with task polling
4. **QA Agent** - Validates image quality, aspect ratio, and Arabic legibility
5. **Export Agent** - Uploads validated images to Google Drive

## Features

- ✅ Complete KIE API integration (NO direct Nano Banana API calls)
- ✅ Sequential workflow with quality gates
- ✅ Automatic task polling and status monitoring
- ✅ Image quality validation (aspect ratio, clarity, Arabic legibility)
- ✅ Google Drive export with Service Account authentication
- ✅ Production-ready deployment configuration
- ✅ Compatible with agencii.ai dashboard

## Installation

1. **Clone and navigate to the project:**
   ```bash
   cd /workspace
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables:**
   ```bash
   cp .env.template .env
   # Edit .env with your API keys
   ```

## Environment Variables

Required environment variables (set in `.env`):

- `OPENAI_API_KEY` - OpenAI API key (required)
- `KIE_API_KEY` - KIE API key for image generation (required)
- `KIE_API_BASE` - KIE API base URL (default: `https://api.kie.ai/api/v1`)
- `GOOGLE_SERVICE_ACCOUNT_JSON` - Google Service Account JSON (base64-encoded or raw JSON) (required for export)
- `GDRIVE_FOLDER_ID` - Google Drive folder ID for uploads (required for export)

## Usage

### Local Development

```bash
python main.py
```

The API will be available at `http://localhost:8080`

### Terminal Demo

```bash
python agency.py
```

### Deployment to agencii.ai

1. **Prepare deployment:**
   ```bash
   ./deployment.sh
   ```

2. **Deploy via agencii CLI or dashboard:**
   - Use the `agencii.json` configuration file
   - Ensure all environment variables are set in the deployment environment

## Workflow

The system follows a sequential pipeline:

```
User Input
    ↓
Brief Agent (extract theme, tone, palette)
    ↓
Art Direction Agent (create Nano Banana prompt)
    ↓
NB Image Agent (generate via KIE API)
    ↓
QA Agent (validate quality)
    ↓
Export Agent (upload to Google Drive)
    ↓
Final Result (JSON with image URLs)
```

If QA validation fails, the system returns retry status with correction notes.

## API Endpoints

### Generate Image

```bash
POST /generate
Content-Type: application/json

{
  "message": "Create a peaceful image with Arabic text about meditation"
}
```

Response:
```json
{
  "theme": "meditation",
  "prompt_used": "A cinematic minimalistic artwork...",
  "image_url": "https://...",
  "gdrive_url": "https://drive.google.com/...",
  "seed": "12345",
  "aspect_ratio": "16:9"
}
```

## Project Structure

```
/workspace
├── brief_agent/
│   ├── brief_agent.py
│   ├── instructions.md
│   └── tools/
├── art_direction_agent/
│   ├── art_direction_agent.py
│   ├── instructions.md
│   └── tools/
├── nb_image_agent/
│   ├── nb_image_agent.py
│   ├── instructions.md
│   └── tools/
│       └── kie_nano_banana.py
├── qa_agent/
│   ├── qa_agent.py
│   ├── instructions.md
│   └── tools/
│       └── validation.py
├── export_agent/
│   ├── export_agent.py
│   ├── instructions.md
│   └── tools/
│       └── gdrive_upload.py
├── agency.py
├── main.py
├── shared_instructions.md
├── requirements.txt
├── agencii.json
├── deployment.sh
└── .env.template
```

## Tools

### KIE Nano Banana (`kie_nano_banana.py`)
- Submits image generation tasks via KIE API
- Polls task status until completion
- Extracts image URLs and metadata
- Includes retry logic and error handling

### Google Drive Upload (`gdrive_upload.py`)
- Uploads images using Service Account authentication
- Generates sharing URLs (view and download)
- Handles OAuth 2.0 JWT flow automatically

### Validation (`validation.py`)
- Checks aspect ratio correctness (5% tolerance)
- Validates image clarity and sharpness
- Detects distortion and artifacts
- Verifies Arabic text legibility

## Art Direction Template

The system uses a standardized prompt template for Athar-style images:

```
A cinematic minimalistic artwork inspired by Athar.
Theme: {{theme}}
Mood: {{mood}}
Palette: {{palette}}
Visual Metaphor: {{element}}
Composition:
  Soft foreground subject with gentle depth.
  Background atmospheric texture with paper grain and cinematic lighting.
Tone: poetic, calm, meditative.
Avoid: messy textures, chaotic shapes, distorted Arabic text.
--ar {{aspect_ratio}}
--style cinematic-premium
```

## Testing

Test individual tools:

```bash
# Test KIE integration
python nb_image_agent/tools/kie_nano_banana.py

# Test validation
python qa_agent/tools/validation.py

# Test Google Drive upload
python export_agent/tools/gdrive_upload.py
```

## License

MIT

## Support

For issues or questions, refer to:
- [Agency Swarm Documentation](https://agency-swarm.ai)
- [KIE API Documentation](https://api.kie.ai/docs)
