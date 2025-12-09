# Configuration

Pynidus provides a `ConfigService` to manage application configuration using Pydantic models.

## Defining Configuration

Define your settings by extending `BaseSettings` (which wraps `pydantic-settings`).

```python
from pynidus.core.config import BaseSettings
from pydantic import Field

class AppSettings(BaseSettings):
    app_name: str = "MyApp"
    database_url: str = Field(..., alias="DATABASE_URL")
    
    model_config = {
        "env_file": ".env"
    }
```

## Accessing Configuration

Inject `ConfigService` into your services.

```python
from pynidus import Injectable
from pynidus.core.config import ConfigService
from .config import AppSettings

@Injectable()
class MyService:
    def __init__(self, config_service: ConfigService[AppSettings]):
        self.settings = config_service.get()
        print(self.settings.app_name)
```

## Built-in Configuration

Pynidus comes with built-in configuration for OAuth2.

```python
class OAuth2Config(BaseModel):
    enabled: bool = False
    secret_key: str = "secret"
    algorithm: str = "HS256"
    audience: Optional[str] = None
    issuer: Optional[str] = None
```

To enable it, set environment variables like `OAUTH2__ENABLED=true` and `OAUTH2__SECRET_KEY=mykey`.
