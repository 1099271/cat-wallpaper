# cat-wallpaper

Monorepo MVP: FastAPI + Next.js to generate wallpaper images and short videos.

See `docs/CONFIGURATION.md` for architecture and configuration details.
See `docs/EXAMPLES.md` for smoke tests and curl examples.

## Requirements
- Python 3.11+
- uv
- pnpm

## Setup
```bash
pnpm install
```

## Scripts
```bash
./scripts/start.sh    # start API + Web
./scripts/stop.sh     # stop API + Web
./scripts/restart.sh  # restart API + Web
```

### API
```bash
cd apps/api
cp .env.example .env
uv venv .venv
uv pip install -e '.[dev]'
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

### Web
```bash
cd apps/web
cp .env.example .env
pnpm dev
```

## Notes
- API serves generated files at `/static/...`.
- Default API base in web is `http://localhost:8000`.
