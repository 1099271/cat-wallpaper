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
