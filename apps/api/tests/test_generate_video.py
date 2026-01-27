import os
from pathlib import Path

from fastapi.testclient import TestClient

os.environ.setdefault("FAL_API_KEY", "test-key")
os.environ.setdefault("FAL_IMAGE_MODEL_ID", "test-image-model")
os.environ.setdefault("FAL_VIDEO_MODEL_ID", "test-video-model")

from app.main import app  # noqa: E402
from app.settings import settings  # noqa: E402


def test_generate_video_happy_path(monkeypatch):
    job_id = "job-123"
    image_dir = Path(settings.storage_root, "images", job_id)
    image_dir.mkdir(parents=True, exist_ok=True)
    image_path = image_dir / "image-1.png"
    image_path.write_bytes(b"fake-image")

    def fake_generate_video(path, ratio):
        assert path == image_path
        return ("video.mp4", b"video-bytes")

    monkeypatch.setattr("app.main.generate_video", fake_generate_video)
    client = TestClient(app)
    resp = client.post(
        "/api/generate-video",
        json={
            "job_id": job_id,
            "image_url": f"/static/images/{job_id}/image-1.png",
            "aspect_ratio": "16:9",
        },
    )
    assert resp.status_code == 200
    payload = resp.json()
    assert payload["video_url"].endswith(f"/static/videos/{job_id}/video.mp4")
    video_path = Path(settings.storage_root, "videos", job_id, "video.mp4")
    assert video_path.exists()
