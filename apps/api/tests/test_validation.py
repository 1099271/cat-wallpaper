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


def test_rejects_invalid_extension():
    client = TestClient(app)
    files = [("files", ("a.gif", b"fake", "image/gif"))]
    resp = client.post("/api/generate-image", files=files)
    assert resp.status_code == 400


def test_rejects_too_large_file():
    client = TestClient(app)
    payload = b"a" * (20 * 1024 * 1024 + 1)
    files = [("files", ("a.jpg", payload, "image/jpeg"))]
    resp = client.post("/api/generate-image", files=files)
    assert resp.status_code == 400
