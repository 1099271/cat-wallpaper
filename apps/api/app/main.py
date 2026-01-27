from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.staticfiles import StaticFiles

from .fal_client import generate_images
from .settings import settings
from .storage import ensure_storage_dirs, job_dir, new_job_id
from .validation import validate_uploads

app = FastAPI()
ensure_storage_dirs(settings.storage_root)
app.mount("/static", StaticFiles(directory=settings.storage_root), name="static")


@app.post("/api/generate-image")
async def generate_image(
    files: list[UploadFile] = File(...),
    prompt: str | None = Form(None),
    image_count: int | None = Form(None),
    aspect_ratio: str | None = Form(None),
):
    validate_uploads(files)
    job_id = new_job_id()
    uploads_dir = job_dir(settings.storage_root, "uploads", job_id)
    images_dir = job_dir(settings.storage_root, "images", job_id)
    uploads_dir.mkdir(parents=True, exist_ok=True)
    images_dir.mkdir(parents=True, exist_ok=True)

    upload_paths: list[Path] = []
    for file in files:
        filename = Path(file.filename or "upload").name
        target = uploads_dir / filename
        content = await file.read()
        target.write_bytes(content)
        upload_paths.append(target)

    prompt_used = prompt.strip() if prompt and prompt.strip() else settings.default_prompt
    count = image_count or settings.default_image_count
    ratio = aspect_ratio or "16:9"

    try:
        generated = generate_images(prompt_used, count, ratio, upload_paths)
    except Exception as exc:  # pragma: no cover - external service
        raise HTTPException(status_code=502, detail="Image generation failed.") from exc

    image_urls: list[str] = []
    for name, content in generated:
        safe_name = Path(name).name or "image.png"
        dest = images_dir / safe_name
        dest.write_bytes(content)
        image_urls.append(f"/static/images/{job_id}/{safe_name}")

    return {"job_id": job_id, "images": image_urls, "prompt_used": prompt_used}
