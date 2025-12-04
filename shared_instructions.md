# Background

## Agency Overview

The Athar Image Designer Swarm is a production-ready multi-agent system designed to generate high-quality cinematic Athar-style images using Nano Banana Pro via the KIE API. The system orchestrates a sequential workflow from creative brief extraction through image generation, quality assurance, and final export to Google Drive.

## Business Context

This agency specializes in creating cinematic minimalistic artwork inspired by Athar's aesthetic - characterized by poetic calmness, meditative tones, and atmospheric textures with paper grain and cinematic lighting.

## Target Audience

Users seeking high-quality, cinematic minimalistic images with Arabic text integration, suitable for artistic, spiritual, or meditative content creation.

## Technical Environment

- **Image Generation**: Nano Banana Pro via KIE API (NOT direct Nano Banana API)
- **Storage**: Google Drive using Service Account authentication
- **API Endpoints**: 
  - POST `/api/v1/playground/createTask` - Submit image generation tasks
  - GET `/api/v1/playground/recordInfo?taskId=xxxx` - Poll task status
- **Workflow**: Sequential pipeline (brief → art direction → image generation → QA → export)

## Key Constraints

- All image generation requests MUST go through KIE API endpoints only
- Images must maintain Athar's cinematic minimalistic aesthetic
- Arabic text must be legible and properly rendered
- Aspect ratios must be accurate (within 5% tolerance)
- All outputs must be production-quality

## Agent Roles

1. **BriefAgent**: Extracts theme, tone, palette, and keywords from user input
2. **ArtDirectionAgent**: Converts briefs into complete Nano Banana prompts
3. **NbImageAgent**: Generates images via KIE API with task polling
4. **QaAgent**: Validates image quality, aspect ratio, clarity, and Arabic legibility
5. **ExportAgent**: Uploads validated images to Google Drive

## Workflow Pattern

The system follows a sequential pipeline where each agent passes results to the next:
brief_agent → art_direction_agent → nb_image_agent → qa_agent → export_agent

If QA validation fails, the system should retry with correction notes.
