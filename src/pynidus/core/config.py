from pydantic_settings import BaseSettings as PydanticBaseSettings
from pydantic import BaseModel, Field
from pynidus.common.decorators.injectable import Injectable
from typing import TypeVar, Generic, Type

T = TypeVar("T", bound=PydanticBaseSettings)

class BaseSettings(PydanticBaseSettings):
    """
    Base class for application settings.
    Reads from environment variables and .env files.
    """
    oauth2: "OAuth2Config" = Field(default_factory=lambda: OAuth2Config())

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        env_file_encoding = "utf-8"
        extra = "ignore"
        env_nested_delimiter = "__"

class OAuth2Config(BaseModel):
    enabled: bool = False
    secret_key: str = "secret"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30


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
