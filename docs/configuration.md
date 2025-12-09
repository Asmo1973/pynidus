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


## Server Configuration

Pynidus simplifies uvicorn configuration via `ServerConfig`. The default prefix is `SERVER__`.

| Variable | Default | Description |
|----------|---------|-------------|
| `SERVER__HOST` | `0.0.0.0` | Bind host |
| `SERVER__PORT` | `3000` | Bind port |
| `SERVER__SSL_KEYFILE` | `None` | Path to SSL key file |
| `SERVER__SSL_CERTFILE` | `None` | Path to SSL cert file |

To use this configuration, start your app with `NidusFactory.listen`:

```python
from pynidus import NidusFactory

# Starts uvicorn with settings from env or defaults
NidusFactory.listen(AppModule)
```

You can also override settings programmatically:

```python
NidusFactory.listen(AppModule, port=8080)
```
