import os

from fastapi.testclient import TestClient

os.environ.setdefault("FAL_API_KEY", "test-key")
os.environ.setdefault("FAL_IMAGE_MODEL_ID", "test-image-model")
os.environ.setdefault("FAL_VIDEO_MODEL_ID", "test-video-model")

from app.main import app  # noqa: E402


def test_rejects_too_many_files():
    client = TestClient(app)
    files = [("files", ("a.jpg", b"fake", "image/jpeg")) for _ in range(6)]
    resp = client.post("/api/generate-image", files=files)
    assert resp.status_code == 400
