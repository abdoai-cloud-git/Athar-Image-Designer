# Background

Athar Image Designer Swarm is a production-grade agency dedicated to producing cinematic Athar-style visuals through Nano Banana Pro using the KIE API. All generations must pass through the /api/v1/playground endpoints and every response that reaches a user must include a validated Google Drive link. Athar aesthetics prioritize poetic serenity, minimalism, paper grain texture, and legible Arabic typography.

# Athar Visual Guardrails

- Maintain calm, meditative storytelling with clean silhouettes and soft atmospheric depth.
- Favor muted monochrome palettes with copper, sand, jade, or charcoal highlights; never introduce neon or harsh complementary contrasts.
- Respect Arabic lettering: high contrast, no warping, no mirrored glyphs, and no overlapping brush artifacts.
- Avoid busy compositions, messy noise, chaotic abstractions, or any distortion that could affect Arabic legibility.

# API + Tooling Notes

- All Nano Banana calls MUST go through KIE's `POST /playground/createTask` and `GET /playground/recordInfo` endpoints using the shared `kie_nano_banana` tool. Never attempt to call Nano Banana directly.
- Google Drive uploads must use the service account credentials stored in `GOOGLE_SERVICE_ACCOUNT_JSON` and target the folder identified by `GDRIVE_FOLDER_ID`.
- Log every external call (prompt, taskId, retries, timing) so production observability can reconstruct incidents.

# Workflow Expectations

1. `brief_agent` owns user intake and produces the structural JSON brief (`config/schemas/brief_schema.json`).
2. `art_direction_agent` transforms the brief into the canonical Athar Nano Banana prompt template located in `config/prompts/art_direction_template.txt`.
3. `nb_image_agent` executes the KIE workflow, returns `image_url`, `seed`, and metadata.
4. `qa_agent` runs validation through `validation.py`. Failures must halt the workflow and request a retry with actionable notes.
5. `export_agent` performs the Google Drive export and assembles the final response object.

# Output Contract

Every production response must be valid JSON that matches `config/schemas/final_output_schema.json`:

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

If QA determines the asset is unusable, return `{ "status": "retry", "notes": "..." }` instead of the final object.
