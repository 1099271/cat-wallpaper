# Configuration and Architecture Guide

This document summarizes the MVP architecture, runtime flow, and required configuration.

## Overview
- Monorepo with pnpm + uv.
- Frontend: Next.js App Router (`apps/web`).
- Backend: FastAPI (`apps/api`).
- Storage: local disk under `storage/`, served via `/static`.

## Repository Layout
```
apps/
  api/                     # FastAPI service
  web/                     # Next.js app
packages/
  shared/                  # Shared constants
storage/
  uploads/
  images/
  videos/
```

## Runtime Flow
1. User uploads 1-5 images in the web UI.
2. Web sends a `multipart/form-data` request to `/api/generate-image`.
3. API saves uploads to `storage/uploads/<job_id>/`.
4. API calls fal.ai image model, saves outputs to `storage/images/<job_id>/`.
5. Web shows generated images and user selects one.
6. Web sends JSON request to `/api/generate-video`.
7. API calls fal.ai video model, saves output to `storage/videos/<job_id>/`.
8. Web previews the video via `/static/...` URL.

## API Endpoints
### POST /api/generate-image
Request (multipart/form-data):
- files: list of image files (1-5)
- prompt: string (optional)
- image_count: integer (optional, default 4)
- aspect_ratio: string (optional, default "16:9")

Response:
```json
{
  "job_id": "string",
  "images": ["/static/images/<job_id>/image-1.png"],
  "prompt_used": "string"
}
```

### POST /api/generate-video
Request (JSON):
```json
{
  "job_id": "string",
  "image_url": "/static/images/<job_id>/image-1.png",
  "aspect_ratio": "16:9"
}
```

Response:
```json
{
  "job_id": "string",
  "video_url": "/static/videos/<job_id>/video.mp4"
}
```

## Environment Variables
### apps/api/.env
```
FAL_API_KEY=your_key
FAL_IMAGE_MODEL_ID=fal-ai/nano-banana-pro/edit
FAL_VIDEO_MODEL_ID=fal-ai/kling-video/v2.6/standard/motion-control
```

### apps/web/.env
```
NEXT_PUBLIC_API_BASE=http://localhost:8000
```

## fal.ai Model Payloads
### Image-to-Image: fal-ai/nano-banana-pro/edit
Context7 docs show these request fields:
- prompt (string, required)
- image_urls (list<string>, required)
- num_images (int, optional, default 1, 1-4)
- aspect_ratio (optional, default "auto")
- output_format (optional: png/jpeg/webp)
- resolution (optional: "1K" | "2K" | "4K")
- sync_mode (optional)

Response:
```json
{
  "images": [
    { "file_name": "output.png", "content_type": "image/png", "url": "..." }
  ],
  "description": ""
}
```

### Image-to-Video: fal-ai/kling-video/v2.6/standard/motion-control
Context7 did not return the exact schema for this model version. Based on other Kling models,
inputs typically include:
- prompt (string, required)
- image_url (string, required)
- aspect_ratio (optional)
- duration or motion controls (model-specific)

**Action required:** verify the exact payload and response shape on the model page:
`https://fal.ai/models/fal-ai/kling-video/v2.6/standard/motion-control`.

Once confirmed, update `apps/api/app/fal_client.py` to map fields correctly.

## Storage and Static Files
- Uploads: `storage/uploads/<job_id>/`
- Images: `storage/images/<job_id>/`
- Videos: `storage/videos/<job_id>/`
- Served under `/static/...` from FastAPI.

## Local Development
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
- If the API base is not localhost, update `NEXT_PUBLIC_API_BASE`.
- For production, replace local storage with object storage and add async jobs.
