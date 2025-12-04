# Athar Image Designer Swarm

A production-ready multi-agent system that generates cinematic Athar-style imagery through Nano Banana Pro via the KIE playground API, validates quality, and delivers assets through Google Drive for agencii.ai deployments.

## Features
- Structured briefing, art direction, KIE Nano Banana execution, QA, and export agents.
- Hardened wrappers for `POST /playground/createTask` and `GET /playground/recordInfo` with retries and polling.
- Google Drive service-account uploader with public share links.
- Validation heuristics for aspect ratio, clarity, and Arabic legibility.
- Workflow configuration (`workflows/generate_athar_image.yaml`) and deployment metadata (`agencii.json`).

## Folder Layout
```
athar_image_designer/
├── agents/
│   ├── *.py                # Agent objects
│   └── instructions/*.md   # Agent-specific instructions
├── tools/
│   ├── kie_nano_banana.py
│   ├── gdrive_upload.py
│   └── validation.py
├── config/
│   ├── prompts/
│   └── schemas/
├── workflows/generate_athar_image.yaml
├── main.py
├── agencii.json
├── README.md
└── deployment.sh
```

## Environment Variables
Set these in `.env`:
- `OPENAI_API_KEY`
- `KIE_API_KEY`
- `KIE_API_BASE` (default `https://api.kie.ai/api/v1`)
- `GOOGLE_SERVICE_ACCOUNT_JSON` (JSON blob or path)
- `GDRIVE_FOLDER_ID`

## Local Workflow Test
```
source .venv/bin/activate
python -m athar_image_designer.main "Write prompt here"
```

## Deployment (agencii)
1. Ensure `agencii` CLI is installed and authenticated.
2. Run `./athar_image_designer/deployment.sh` (makes use of `agencii.json`).
3. Monitor logs from the agencii dashboard; tracing and logging are enabled by default.

## Output Contract
Final responses must match `config/schemas/final_output_schema.json`:
```
{
  "theme": "",
  "prompt_used": "",
  "image_url": "",
  "gdrive_url": "",
  "seed": "",
  "aspect_ratio": ""
}
```
If QA fails a render, the agency must return `{ "status": "retry", "notes": [...] }` instead.
