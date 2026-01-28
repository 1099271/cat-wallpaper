from pathlib import Path

from pydantic_settings import BaseSettings

ROOT_DIR = Path(__file__).resolve().parents[3]
DEFAULT_STORAGE_ROOT = str(ROOT_DIR / "storage")


class Settings(BaseSettings):
    fal_api_key: str
    fal_image_model_id: str
    fal_video_model_id: str
    default_prompt: str = "Use these photos as reference to generate a cinematic wallpaper."
    default_image_count: int = 4
    storage_root: str = DEFAULT_STORAGE_ROOT


settings = Settings()
