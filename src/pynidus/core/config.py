from pydantic_settings import BaseSettings as PydanticBaseSettings
from pydantic import BaseModel, Field
from pynidus.common.decorators.injectable import Injectable
from typing import TypeVar, Generic, Type, Optional

T = TypeVar("T", bound=PydanticBaseSettings)

class OAuth2Config(BaseModel):
    enabled: bool = False
    secret_key: str = "secret"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    audience: Optional[str] = None
    issuer: Optional[str] = None

class ServerConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 3000
    ssl_keyfile: Optional[str] = None
    ssl_certfile: Optional[str] = None

class BaseSettings(PydanticBaseSettings):
    """
    Base class for application settings.
    Reads from environment variables and .env files.
    """
    oauth2: OAuth2Config = Field(default_factory=lambda: OAuth2Config())
    server: ServerConfig = Field(default_factory=lambda: ServerConfig())

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
        "env_nested_delimiter": "__"
    }

@Injectable()
class ConfigService(Generic[T]):
    """
    Service to provide configuration settings.
    Usage:
        @Injectable()
        class MyService:
            def __init__(self, config: ConfigService[AppSettings]):
                self.settings = config.get()
    """
    def __init__(self, settings_cls: Type[T] = BaseSettings):
        self._settings = settings_cls()

    def get(self) -> T:
        return self._settings
