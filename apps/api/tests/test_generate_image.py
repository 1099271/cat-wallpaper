import os
from pathlib import Path

from fastapi.testclient import TestClient

os.environ.setdefault("FAL_API_KEY", "test-key")
os.environ.setdefault("FAL_IMAGE_MODEL_ID", "test-image-model")
os.environ.setdefault("FAL_VIDEO_MODEL_ID", "test-video-model")

from app.main import app  # noqa: E402
from app.settings import settings  # noqa: E402


def test_generate_image_happy_path(monkeypatch):
    def fake_generate_images(prompt, count, ratio, image_paths):
        return [("image-1.png", b"image-bytes")]

    monkeypatch.setattr("app.main.generate_images", fake_generate_images)
    client = TestClient(app)
    files = [("files", ("a.jpg", b"fake", "image/jpeg"))]
    resp = client.post(
        "/api/generate-image",
        data={"prompt": "hello", "image_count": "1", "aspect_ratio": "16:9"},
        files=files,
    )
    assert resp.status_code == 200
    payload = resp.json()
    assert payload["prompt_used"] == "hello"
    assert payload["images"]
    image_path = Path(settings.storage_root, "images", payload["job_id"], "image-1.png")
    assert image_path.exists()
