from app.settings import settings


def build_image_payload(prompt: str, count: int, aspect_ratio: str) -> dict:
    return {"prompt": prompt, "num_images": count, "aspect_ratio": aspect_ratio}
