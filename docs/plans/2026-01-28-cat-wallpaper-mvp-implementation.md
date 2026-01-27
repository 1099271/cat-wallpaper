# Cat Wallpaper MVP Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a monorepo MVP with Next.js (App Router) + FastAPI that uploads 1-5 photos, generates images via fal.ai, then generates a short video from a selected image.

**Architecture:** pnpm workspaces manage `apps/web` (Next.js) and `packages/shared` (types/config). Python backend lives in `apps/api` with uv-managed deps, serving static files from local storage. Frontend calls backend APIs to generate images and videos synchronously.

**Tech Stack:** Next.js 15 (App Router), React, TypeScript, FastAPI, Pydantic, uvicorn, uv, fal-client, pnpm.

---

### Task 1: Scaffold the monorepo workspace

**Files:**
- Create: `pnpm-workspace.yaml`
- Create: `package.json`
- Create: `apps/web/package.json`
- Create: `packages/shared/package.json`
- Create: `packages/shared/tsconfig.json`

**Step 1: Create workspace config**

Create `pnpm-workspace.yaml`:
```yaml
packages:
  - "apps/*"
  - "packages/*"
```

**Step 2: Create root package.json**
```json
{
  "name": "cat-wallpaper",
  "private": true,
  "packageManager": "pnpm@9.15.0",
  "scripts": {
    "dev": "pnpm -r dev",
    "build": "pnpm -r build",
    "lint": "pnpm -r lint"
  }
}
```

**Step 3: Create shared package skeleton**
`packages/shared/package.json`:
```json
{
  "name": "@cat-wallpaper/shared",
  "version": "0.1.0",
  "private": true,
  "type": "module",
  "exports": {
    ".": "./src/index.ts"
  }
}
```
`packages/shared/tsconfig.json`:
```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "Bundler",
    "strict": true,
    "noEmit": true
  },
  "include": ["src"]
}
```

**Step 4: Create placeholder packages**
`apps/web/package.json`:
```json
{
  "name": "web",
  "private": true
}
```

**Step 5: Commit**
Run:
```
git add pnpm-workspace.yaml package.json apps/web/package.json packages/shared/package.json packages/shared/tsconfig.json
git commit -m "chore: scaffold monorepo workspace"
```

---

### Task 2: Add shared constants and types

**Files:**
- Create: `packages/shared/src/index.ts`

**Step 1: Write minimal constants**
```ts
export const MAX_UPLOAD_COUNT = 5;
export const MAX_FILE_SIZE_MB = 20;
export const ALLOWED_EXTENSIONS = ["jpg", "jpeg", "png", "webp"] as const;
export const DEFAULT_IMAGE_COUNT = 4;
export const ASPECT_RATIOS = ["16:9", "9:16"] as const;
export type AspectRatio = (typeof ASPECT_RATIOS)[number];
```

**Step 2: Commit**
Run:
```
git add packages/shared/src/index.ts
git commit -m "feat(shared): add MVP constants"
```

---

### Task 3: Scaffold FastAPI app with uv

**Files:**
- Create: `apps/api/pyproject.toml`
- Create: `apps/api/app/main.py`
- Create: `apps/api/app/settings.py`
- Create: `apps/api/app/storage.py`
- Create: `apps/api/app/__init__.py`

**Step 1: Create pyproject**
```toml
[project]
name = "cat-wallpaper-api"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
  "fastapi>=0.115.0",
  "uvicorn>=0.30.0",
  "python-multipart>=0.0.9",
  "pydantic>=2.7.0",
  "pydantic-settings>=2.3.0",
  "fal-client>=0.4.0",
]

[project.optional-dependencies]
dev = ["pytest>=8.0.0", "httpx>=0.27.0"]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

**Step 2: Create settings**
`apps/api/app/settings.py`:
```python
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    fal_api_key: str
    fal_image_model_id: str
    fal_video_model_id: str
    default_prompt: str = "Use these photos as reference to generate a cinematic wallpaper."
    default_image_count: int = 4
    storage_root: str = "storage"


settings = Settings()
```

**Step 3: Create storage helpers**
`apps/api/app/storage.py`:
```python
from pathlib import Path
import uuid


def ensure_storage_dirs(root: str) -> None:
    for name in ("uploads", "images", "videos"):
        Path(root, name).mkdir(parents=True, exist_ok=True)


def new_job_id() -> str:
    return uuid.uuid4().hex


def job_dir(root: str, kind: str, job_id: str) -> Path:
    return Path(root, kind, job_id)
```

**Step 4: Create FastAPI app skeleton**
`apps/api/app/main.py`:
```python
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from .settings import settings
from .storage import ensure_storage_dirs

app = FastAPI()
ensure_storage_dirs(settings.storage_root)
app.mount("/static", StaticFiles(directory=settings.storage_root), name="static")
```

**Step 5: Commit**
Run:
```
git add apps/api/pyproject.toml apps/api/app
git commit -m "chore(api): scaffold fastapi app"
```

---

### Task 4: Add upload validation tests (TDD)

**Files:**
- Create: `apps/api/tests/test_validation.py`
- Modify: `apps/api/app/main.py`
- Create: `apps/api/app/validation.py`

**Step 1: Write failing tests**
```python
from fastapi.testclient import TestClient
from app.main import app


def test_rejects_too_many_files():
    client = TestClient(app)
    files = [("files", ("a.jpg", b"fake", "image/jpeg")) for _ in range(6)]
    resp = client.post("/api/generate-image", files=files)
    assert resp.status_code == 400
```

**Step 2: Run test to verify it fails**
Run: `pytest apps/api/tests/test_validation.py::test_rejects_too_many_files -v`
Expected: FAIL (route not found or validation missing).

**Step 3: Implement minimal validation**
Create `apps/api/app/validation.py`:
```python
from pathlib import Path
from typing import Iterable

from fastapi import HTTPException, UploadFile

ALLOWED_EXTS = {"jpg", "jpeg", "png", "webp"}
MAX_COUNT = 5
MAX_MB = 20


def validate_uploads(files: Iterable[UploadFile]) -> None:
    files = list(files)
    if len(files) < 1 or len(files) > MAX_COUNT:
        raise HTTPException(status_code=400, detail="Invalid file count.")
    for file in files:
        ext = Path(file.filename or "").suffix.lower().lstrip(".")
        if ext not in ALLOWED_EXTS:
            raise HTTPException(status_code=400, detail="Invalid file type.")
```
Update `apps/api/app/main.py` to add a placeholder endpoint that runs validation:
```python
from fastapi import UploadFile, File
from .validation import validate_uploads

@app.post("/api/generate-image")
async def generate_image(files: list[UploadFile] = File(...)):
    validate_uploads(files)
    return {"ok": True}
```

**Step 4: Run test to verify it passes**
Run: `pytest apps/api/tests/test_validation.py::test_rejects_too_many_files -v`
Expected: PASS.

**Step 5: Commit**
Run:
```
git add apps/api/tests/test_validation.py apps/api/app/validation.py apps/api/app/main.py
git commit -m "test(api): add upload count validation"
```

---

### Task 5: Implement full validation (type + size)

**Files:**
- Modify: `apps/api/tests/test_validation.py`
- Modify: `apps/api/app/validation.py`

**Step 1: Add failing tests**
```python
def test_rejects_invalid_extension():
    client = TestClient(app)
    files = [("files", ("a.gif", b"fake", "image/gif"))]
    resp = client.post("/api/generate-image", files=files)
    assert resp.status_code == 400
```

**Step 2: Run test to verify it fails**
Run: `pytest apps/api/tests/test_validation.py::test_rejects_invalid_extension -v`
Expected: FAIL (not validated).

**Step 3: Implement size/type checks**
Update `validate_uploads`:
```python
    for file in files:
        ext = Path(file.filename or "").suffix.lower().lstrip(".")
        if ext not in ALLOWED_EXTS:
            raise HTTPException(status_code=400, detail="Invalid file type.")
        if file.size is not None and file.size > MAX_MB * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File too large.")
```

**Step 4: Run test to verify it passes**
Run: `pytest apps/api/tests/test_validation.py::test_rejects_invalid_extension -v`
Expected: PASS.

**Step 5: Commit**
Run:
```
git add apps/api/tests/test_validation.py apps/api/app/validation.py
git commit -m "feat(api): validate upload type and size"
```

---

### Task 6: Add fal.ai client wrapper (TDD)

**Files:**
- Create: `apps/api/app/fal_client.py`
- Create: `apps/api/tests/test_fal_client.py`

**Step 1: Write failing test**
```python
from app.fal_client import build_image_payload


def test_build_image_payload_includes_prompt_and_count():
    payload = build_image_payload("hello", 4, "16:9")
    assert payload["prompt"] == "hello"
    assert payload["num_images"] == 4
```

**Step 2: Run test to verify it fails**
Run: `pytest apps/api/tests/test_fal_client.py::test_build_image_payload_includes_prompt_and_count -v`
Expected: FAIL (module missing).

**Step 3: Implement minimal wrapper**
`apps/api/app/fal_client.py`:
```python
from app.settings import settings


def build_image_payload(prompt: str, count: int, aspect_ratio: str) -> dict:
    return {"prompt": prompt, "num_images": count, "aspect_ratio": aspect_ratio}
```

**Step 4: Run test to verify it passes**
Run: `pytest apps/api/tests/test_fal_client.py::test_build_image_payload_includes_prompt_and_count -v`
Expected: PASS.

**Step 5: Commit**
Run:
```
git add apps/api/app/fal_client.py apps/api/tests/test_fal_client.py
git commit -m "feat(api): add fal.ai payload helpers"
```

---

### Task 7: Implement generate-image endpoint (with storage)

**Files:**
- Modify: `apps/api/app/main.py`
- Modify: `apps/api/app/storage.py`
- Modify: `apps/api/app/validation.py`

**Step 1: Add failing test (happy path with mock)**
Create test to mock fal.ai call and verify response URLs. (Use `monkeypatch` to stub a function that returns image URLs.)

**Step 2: Run test to verify it fails**
Run: `pytest apps/api/tests/test_generate_image.py::test_generate_image_happy_path -v`
Expected: FAIL (endpoint not implemented).

**Step 3: Implement endpoint**
Steps:
- Save uploaded files to `storage/uploads/<job_id>/`
- Build prompt (use default if empty)
- Call fal.ai model (via wrapper)
- Save returned image bytes to `storage/images/<job_id>/`
- Return URLs like `/static/images/<job_id>/<file>`

**Step 4: Run tests to verify they pass**
Run: `pytest apps/api/tests/test_generate_image.py -v`
Expected: PASS.

**Step 5: Commit**
Run:
```
git add apps/api/app/main.py apps/api/app/storage.py apps/api/tests/test_generate_image.py
git commit -m "feat(api): generate images endpoint"
```

---

### Task 8: Implement generate-video endpoint

**Files:**
- Modify: `apps/api/app/main.py`
- Create: `apps/api/tests/test_generate_video.py`

**Step 1: Write failing test**
Add a test that posts a selected image URL and gets a video URL back, with fal.ai mocked.

**Step 2: Run test to verify it fails**
Run: `pytest apps/api/tests/test_generate_video.py::test_generate_video_happy_path -v`
Expected: FAIL.

**Step 3: Implement endpoint**
- Accept JSON with `job_id`, `image_url`, `aspect_ratio`
- Download/read the selected image file
- Call fal.ai video model
- Save output to `storage/videos/<job_id>/video.mp4`
- Return `/static/videos/<job_id>/video.mp4`

**Step 4: Run test to verify it passes**
Run: `pytest apps/api/tests/test_generate_video.py -v`
Expected: PASS.

**Step 5: Commit**
Run:
```
git add apps/api/app/main.py apps/api/tests/test_generate_video.py
git commit -m "feat(api): generate video endpoint"
```

---

### Task 9: Scaffold Next.js app

**Files:**
- Create: `apps/web/next.config.js`
- Create: `apps/web/package.json`
- Create: `apps/web/app/layout.tsx`
- Create: `apps/web/app/page.tsx`
- Create: `apps/web/app/globals.css`

**Step 1: Add Next.js dependencies**
Update `apps/web/package.json`:
```json
{
  "name": "web",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint"
  },
  "dependencies": {
    "next": "15.0.0",
    "react": "18.3.1",
    "react-dom": "18.3.1"
  },
  "devDependencies": {
    "typescript": "5.6.3",
    "@types/react": "18.3.3",
    "@types/react-dom": "18.3.0",
    "eslint": "9.9.0",
    "eslint-config-next": "15.0.0"
  }
}
```

**Step 2: Create minimal app files**
`apps/web/app/layout.tsx`:
```tsx
import "./globals.css";

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="zh-CN">
      <body>{children}</body>
    </html>
  );
}
```
`apps/web/app/page.tsx` (placeholder):
```tsx
export default function Page() {
  return <main>Cat Wallpaper</main>;
}
```

**Step 3: Commit**
Run:
```
git add apps/web
git commit -m "chore(web): scaffold next app"
```

---

### Task 10: Implement Web UI flow

**Files:**
- Modify: `apps/web/app/page.tsx`
- Modify: `apps/web/app/globals.css`

**Step 1: Implement form state**
Add state for files, prompt, imageCount, aspectRatio, loading, errors, images list, selected image, video URL.

**Step 2: Implement upload + generate images**
On submit, POST `FormData` to `/api/generate-image` (backend base URL via env). Render results and allow selection.

**Step 3: Implement video generation**
POST JSON to `/api/generate-video` with selected image.

**Step 4: Commit**
Run:
```
git add apps/web/app/page.tsx apps/web/app/globals.css
git commit -m "feat(web): add MVP upload and generation UI"
```

---

### Task 11: Add environment config and README

**Files:**
- Create: `apps/api/.env.example`
- Create: `apps/web/.env.example`
- Modify: `README.md`

**Step 1: Add example env files**
`apps/api/.env.example`:
```
FAL_API_KEY=your_key
FAL_IMAGE_MODEL_ID=your_image_model
FAL_VIDEO_MODEL_ID=your_video_model
```
`apps/web/.env.example`:
```
NEXT_PUBLIC_API_BASE=http://localhost:8000
```

**Step 2: Update README with dev instructions**
Add commands for:
- `uv venv && uv pip install -r` (or `uv pip install -e .`)
- `uvicorn app.main:app --reload`
- `pnpm install` and `pnpm --filter web dev`

**Step 3: Commit**
Run:
```
git add apps/api/.env.example apps/web/.env.example README.md
git commit -m "docs: add env samples and dev instructions"
```

---

Plan complete and saved to `docs/plans/2026-01-28-cat-wallpaper-mvp-implementation.md`. Two execution options:

1. Subagent-Driven (this session) - I dispatch fresh subagent per task, review between tasks, fast iteration  
2. Parallel Session (separate) - Open new session with executing-plans, batch execution with checkpoints

Which approach?
