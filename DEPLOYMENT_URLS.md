# Deployment URLs

- **Frontend**: https://cognitive-canvas-hackathon.vercel.app
- **Backend**: Deployed on Render
- **GitHub**: https://github.com/somyatambi/cognitive-canvas-hackathon

## Setup

**Vercel**: Auto-deploys from GitHub `main` branch. Set `VITE_API_URL` env var to backend URL.

**Render**: Dockerfile deployment with env vars: `OPENROUTER_API_KEY`, `CEREBRAS_API_KEY`, `PORT=8080`

## Endpoints
- `POST /brainstorm` - Generate startup ideas
- `POST /criticize` - Critique ideas
- `POST /roadmap` - Create strategic roadmap
- `POST /tasks` - Generate actionable tasks
- `POST /pitchdeck` - Generate investor pitch deck
