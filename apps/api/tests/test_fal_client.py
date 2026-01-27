import os

os.environ.setdefault("FAL_API_KEY", "test-key")
os.environ.setdefault("FAL_IMAGE_MODEL_ID", "test-image-model")
os.environ.setdefault("FAL_VIDEO_MODEL_ID", "test-video-model")

from app.fal_client import build_image_payload  # noqa: E402


def test_build_image_payload_includes_prompt_and_count():
    payload = build_image_payload("hello", 4, "16:9")
    assert payload["prompt"] == "hello"
    assert payload["num_images"] == 4
