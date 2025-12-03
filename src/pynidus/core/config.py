from pydantic_settings import BaseSettings as PydanticBaseSettings
from pynidus.common.decorators.injectable import Injectable
from typing import TypeVar, Generic, Type

T = TypeVar("T", bound=PydanticBaseSettings)

class BaseSettings(PydanticBaseSettings):
    """
    Base class for application settings.
    Reads from environment variables and .env files.
    """
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

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
