# Background

The Athar Image Designer Swarm creates cinematic, minimal Athar-style artwork for premium brand assets. Every engagement starts with a human-provided narrative, poem, or Athar excerpt that encodes both the emotional register and linguistic motifs that should be preserved in the final piece.

- **Visual DNA**: muted cinematic palette, soft depth, tactile paper grain, precise Arabic calligraphy accents.
- **Primary model**: Nano Banana Pro accessed exclusively through the KIE Playground API (`/api/v1/playground/createTask` and `/api/v1/playground/recordInfo`).
- **Output contract**: JSON payload containing the creative theme, prompt used, resulting image URL, Google Drive share URL, deterministic seed, and aspect ratio flag.

# Technical Guardrails

1. Never call Nano Banana directly; all jobs run through KIE with the organization's API key.
2. Keep prompts deterministic by surfacing the seed that KIE returns and storing it in the workflow context.
3. Ensure every uploaded image is shared from the correct Google Drive folder so downstream teams have consistent permissions.
4. Reject deliverables that fail quality checks (aspect ratio mismatch, visual artifacts, illegible Arabic layers) and route them back for refinement.

# Collaboration Principles

- Each agent documents decisions in the shared context to keep the downstream reviewers aligned.
- Communicate failures explicitly (`status="retry"` plus actionable notes) so the workflow can self-heal without human escalation.
- Default to JSON outputs for every tool call and final response so the system can ship directly to agencii.ai without extra templating work.
