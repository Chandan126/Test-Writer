from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str
    
    # MinIO S3 Configuration
    MINIO_ENDPOINT: str
    MINIO_ACCESS_KEY: str
    MINIO_SECRET_KEY: str
    MINIO_BUCKET: str
    
    # Application
    DEBUG: bool = False
    MAX_FILE_SIZE: int = 10485760  # 10MB in bytes
    ALLOWED_EXTENSIONS: str = "pdf,doc,docx,txt,jpg,jpeg,png"
    
    # API
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Test Writer API"
    
    @property
    def allowed_extensions_list(self) -> List[str]:
        return [ext.strip() for ext in self.ALLOWED_EXTENSIONS.split(",")]
    
    class Config:
        env_file = ".env"


settings = Settings()
