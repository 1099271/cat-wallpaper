from __future__ import annotations

from pathlib import Path
from typing import Iterable
from urllib import request

import fal_client

from app.settings import settings


def build_image_payload(prompt: str, count: int, aspect_ratio: str) -> dict:
    return {"prompt": prompt, "num_images": count, "aspect_ratio": aspect_ratio}


def generate_images(
    prompt: str, count: int, aspect_ratio: str, image_paths: Iterable[Path]
) -> list[tuple[str, bytes]]:
    image_urls = [fal_client.upload_file(path) for path in image_paths]
    payload = build_image_payload(prompt, count, aspect_ratio)
    payload["image_urls"] = image_urls
    result = fal_client.run(settings.fal_image_model_id, payload)
    output_urls = _extract_image_urls(result)
    return [(f"image-{index + 1}.png", _download(url)) for index, url in enumerate(output_urls)]


def _extract_image_urls(result: dict) -> list[str]:
    images = result.get("images") or result.get("output") or []
    urls: list[str] = []
    for item in images:
        if isinstance(item, str):
            urls.append(item)
        elif isinstance(item, dict) and "url" in item:
            urls.append(str(item["url"]))
    return urls


def _download(url: str) -> bytes:
    with request.urlopen(url) as response:
        return response.read()


def build_video_payload(image_url: str, aspect_ratio: str) -> dict:
    return {"image_url": image_url, "aspect_ratio": aspect_ratio}


def generate_video(image_path: Path, aspect_ratio: str) -> tuple[str, bytes]:
    image_url = fal_client.upload_file(image_path)
    payload = build_video_payload(image_url, aspect_ratio)
    result = fal_client.run(settings.fal_video_model_id, payload)
    video_url = _extract_video_url(result)
    return ("video.mp4", _download(video_url))


def _extract_video_url(result: dict) -> str:
    for key in ("video", "url", "output"):
        if key in result:
            value = result[key]
            if isinstance(value, str):
                return value
            if isinstance(value, dict) and "url" in value:
                return str(value["url"])
    raise ValueError("No video URL found in response.")
