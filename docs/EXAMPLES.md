# Example Requests and Smoke Test

This document provides quick example requests to validate the current flow.

## 1) Start Services

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
pnpm install
pnpm dev
```

Open: http://localhost:3000

## 2) curl: Generate Images
```bash
curl -X POST "http://localhost:8000/api/generate-image" \
  -F "files=@/path/to/photo1.jpg" \
  -F "files=@/path/to/photo2.jpg" \
  -F "prompt=cinematic lighting, dreamy atmosphere" \
  -F "image_count=4" \
  -F "aspect_ratio=16:9"
```

Expected response:
```json
{
  "job_id": "string",
  "images": ["/static/images/<job_id>/image-1.png"],
  "prompt_used": "string"
}
```

## 3) curl: Generate Video
Replace `<job_id>` and `<image_path>` with values from the previous response.

```bash
curl -X POST "http://localhost:8000/api/generate-video" \
  -H "Content-Type: application/json" \
  -d '{
    "job_id": "<job_id>",
    "image_url": "/static/images/<job_id>/<image_path>",
    "aspect_ratio": "16:9"
  }'
```

Expected response:
```json
{
  "job_id": "<job_id>",
  "video_url": "/static/videos/<job_id>/video.mp4"
}
```

## 4) Smoke Checklist
- Upload 1-5 images in the web UI.
- Confirm image results render.
- Select an image and generate video.
- Confirm `/static/videos/...` plays in the browser.
