from fastapi import FastAPI, File, UploadFile
from fastapi.staticfiles import StaticFiles

from .settings import settings
from .storage import ensure_storage_dirs
from .validation import validate_uploads

app = FastAPI()
ensure_storage_dirs(settings.storage_root)
app.mount("/static", StaticFiles(directory=settings.storage_root), name="static")


@app.post("/api/generate-image")
async def generate_image(files: list[UploadFile] = File(...)):
    validate_uploads(files)
    return {"ok": True}
