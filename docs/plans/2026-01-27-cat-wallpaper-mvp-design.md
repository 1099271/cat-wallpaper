# Cat Wallpaper MVP Design

Date: 2026-01-27

## Goals
- Build a monorepo MVP that lets users upload 1-5 photos, optionally provide a prompt, generate multiple images via fal.ai, then generate a short video (3-5 seconds) from a selected image.
- Use Python + FastAPI for backend, Next.js (App Router, Next 15 stable) for frontend, pnpm for JS workspace, uv for Python env/deps.
- Keep everything local: store uploads, generated images, and videos on disk and serve via static URLs.

## Non-Goals (MVP)
- User accounts, history, and persistence beyond local files.
- Asynchronous job processing, queues, or progress tracking.
- Object storage integration (S3, etc).

## Monorepo Structure
```
.
├── apps/
│   ├── api/                 # FastAPI service
│   └── web/                 # Next.js 15 App Router
├── packages/
│   └── shared/              # Shared types/config/helpers
├── storage/
│   ├── uploads/
│   ├── images/
│   └── videos/
├── pnpm-workspace.yaml
└── README.md
```

## Frontend (apps/web)
- Single page flow: upload (1-5 images), choose aspect ratio (16:9 or 9:16), optional prompt, set image count (default 4), submit.
- Show loading states for each generation step.
- Display generated images; user selects one to generate video.
- Constraints enforced client-side:
  - File types: JPG/PNG/WEBP
  - Size: <= 20 MB each
  - Count: 1-5 images

## Backend (apps/api)
- FastAPI endpoints (sync for MVP):
  - `POST /api/generate-image`
    - multipart/form-data: files[] (1-5), prompt (optional), image_count (default 4), aspect_ratio (16:9 or 9:16)
    - Saves uploads to `storage/uploads/<job_id>/`
    - Calls fal.ai image model to generate N images
    - Saves outputs to `storage/images/<job_id>/`
    - Returns: `{ job_id, images: [url, ...], prompt_used }`
  - `POST /api/generate-video`
    - json: `{ job_id, image_url, aspect_ratio }`
    - Uses selected image to call fal.ai video model
    - Saves output to `storage/videos/<job_id>/`
    - Returns: `{ job_id, video_url }`
  - `GET /static/...` serves files from `storage/`
- Validation (server-side):
  - Count, size, and extension checks
  - Reject invalid inputs with 400s
- Error handling:
  - fal.ai errors -> 502
  - Timeouts -> 504
  - File IO -> 500

## Shared Package (packages/shared)
- Shared constants:
  - file limits, defaults, aspect ratios
- Optional: typed API responses, simple fetch helpers for the frontend.

## fal.ai Integration
- Config via environment variables:
  - `FAL_API_KEY`
  - `FAL_IMAGE_MODEL_ID`
  - `FAL_VIDEO_MODEL_ID`
  - `DEFAULT_IMAGE_COUNT=4`
  - `DEFAULT_ASPECT_RATIO=16:9`
- Prompt behavior:
  - Optional. If empty, backend uses a default template.

## Storage
- Local disk storage:
  - uploads: `storage/uploads/<job_id>/`
  - images: `storage/images/<job_id>/`
  - videos: `storage/videos/<job_id>/`
- FastAPI static mount to serve `storage/` paths under `/static`.

## Testing (MVP)
- Backend: pytest happy-path using fal.ai client mocking.
- Frontend: optional minimal form validation tests (can defer).

## Risks / Future Work
- Sync requests may time out with large models; move to async jobs + polling later.
- Replace local storage with S3-compatible storage for production.
- Add history, login, and rate limiting.
