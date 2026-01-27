from pathlib import Path
import uuid


def ensure_storage_dirs(root: str) -> None:
    for name in ("uploads", "images", "videos"):
        Path(root, name).mkdir(parents=True, exist_ok=True)


def new_job_id() -> str:
    return uuid.uuid4().hex


def job_dir(root: str, kind: str, job_id: str) -> Path:
    return Path(root, kind, job_id)
