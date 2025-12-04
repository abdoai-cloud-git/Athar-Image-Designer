# Athar Image Designer Swarm

A production-ready Agency Swarm that generates cinematic Athar-style visuals using Nano Banana Pro (via the KIE Playground API), validates quality, and publishes the approved frame to Google Drive for downstream teams and the agencii.ai dashboard.

## Architecture

- **Agents**: `brief_agent`, `art_direction_agent`, `nb_image_agent`, `qa_agent`, `export_agent` living under `athar_image_designer/agents`.
- **Tools**:
  - `KieNanoBananaTool` – submits `/api/v1/playground/createTask` jobs and polls `/recordInfo` until completion.
  - `ValidationTool` – checks aspect ratio, clarity, and Arabic legibility heuristics.
  - `GDriveUploadTool` – uploads final images using a Google Drive service account.
- **Workflow**: `workflows/generate_athar_image.yaml` wires the agents sequentially.
- **Deployment Assets**: `agencii.json` plus `deployment.sh` configure agencii.ai delivery.

## Environment Variables

Populate `.env` (mirrors `.env.template`):

```
OPENAI_API_KEY=sk-...
KIE_API_KEY=...
KIE_API_BASE=https://api.kie.ai/api/v1
GOOGLE_SERVICE_ACCOUNT_JSON={"type": "service_account", ...}
GDRIVE_FOLDER_ID=xxxxxxxxxxxxxxxxxxxx
```

`GOOGLE_SERVICE_ACCOUNT_JSON` may be a raw JSON string, base64 payload, or filesystem path.

## Local Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Run the FastAPI server (used by agencii.ai):

```bash
python main.py
```

## Testing Individual Tools

```bash
python -m athar_image_designer.tools.kie_nano_banana   # requires KIE env vars
python -m athar_image_designer.tools.validation        # prints helper guidance
python -m athar_image_designer.tools.gdrive_upload     # requires Drive creds
```

## Workflow Contract

The final response published to agencii clients follows `config/schemas/workflow_output_schema.json`:

```json
{
  "theme": "",
  "prompt_used": "",
  "image_url": "",
  "gdrive_url": "",
  "gdrive_download_url": "",
  "filename": "",
  "seed": "",
  "aspect_ratio": "",
  "warnings": []
}
```

QA failures must bubble up as `{ "status": "retry", "notes": "..." }` so the orchestrator can adjust prompts before export.
