"""Settings module with fallback for missing dependencies."""

try:
    from pydantic_settings import BaseSettings
    from pydantic import Field
    PYDANTIC_AVAILABLE = True
except ImportError:
    try:
        from pydantic import BaseSettings, Field
        PYDANTIC_AVAILABLE = True
    except ImportError:
        PYDANTIC_AVAILABLE = False
        # Fallback base class
        class BaseSettings:
            def __init__(self, **kwargs):
                for key, value in kwargs.items():
                    setattr(self, key, value)

        def Field(default=None, **kwargs):
            return default


if PYDANTIC_AVAILABLE:
    class Settings(BaseSettings):
        """Application settings using Pydantic."""
        app_name: str = Field(default="Options Analyzer", env="APP_NAME")
        debug: bool = Field(default=False, env="DEBUG")
        api_key: str = Field(default="", env="API_KEY")
        data_source: str = Field(default="yahoo", env="DATA_SOURCE")

        class Config:
            env_file = ".env"
            env_file_encoding = "utf-8"
else:
    class Settings:
        """Fallback settings class without Pydantic."""
        def __init__(self):
            self.app_name = "Options Analyzer"
            self.debug = False
            self.api_key = ""
            self.data_source = "yahoo"
            print("Warning: Using fallback settings - pydantic not available")


# Create default instance
settings = Settings()
