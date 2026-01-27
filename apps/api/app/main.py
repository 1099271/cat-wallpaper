from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .settings import settings
from .storage import ensure_storage_dirs

app = FastAPI()
ensure_storage_dirs(settings.storage_root)
app.mount("/static", StaticFiles(directory=settings.storage_root), name="static")
