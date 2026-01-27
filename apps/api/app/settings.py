from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    fal_api_key: str
    fal_image_model_id: str
    fal_video_model_id: str
    default_prompt: str = "Use these photos as reference to generate a cinematic wallpaper."
    default_image_count: int = 4
    storage_root: str = "storage"


settings = Settings()
