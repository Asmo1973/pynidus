# Pynidus

Pynidus is a Python library for building scalable microservices, inspired by NestJS. It leverages Python's type hints and decorators to provide a modular and dependency-injection-driven development experience, built on top of FastAPI.

## Installation

```bash
uv add pynidus
```

(Note: Since this is currently a local project, you need to install dependencies manually or use `uv sync`)

## Documentation

Full documentation is available in the [docs/](docs/) directory.

- [Core Concepts](docs/core.md)
- [Configuration](docs/configuration.md)
- [Database](docs/database.md)
- [Security](docs/security.md)
- [Microservices & Events](docs/microservices.md)

## Usage

### 1. Create a Service

```python
from pynidus import Injectable

@Injectable()
class AppService:
    def get_hello(self) -> str:
        return "Hello World from Pynidus!"
```

### 2. Create a Controller

```python
from pynidus import Controller, Get

@Controller()
class AppController:
    def __init__(self, app_service: AppService):
        self.app_service = app_service

    @Get("/")
    def get_hello(self):
        return {"message": self.app_service.get_hello()}
```

### 3. Create a Module

```python
from pynidus import Module

@Module(
    controllers=[AppController],
    providers=[AppService],
)
class AppModule:
    pass
```

### 4. Bootstrap the Application

```python
from pynidus import NestFactory
import uvicorn

def bootstrap():
    app = NestFactory.create(AppModule)
    uvicorn.run(app, host="0.0.0.0", port=3000)

if __name__ == "__main__":
    bootstrap()
```

## Features

- **Dependency Injection**: Built-in DI container to manage your application components.
- **Modularity**: Organize your code into modules.
- **Decorators**: Use decorators like `@Controller`, `@Get`, `@Post`, `@Injectable` to define your application logic.
- **FastAPI**: Built on top of FastAPI for high performance and easy OpenAPI integration.
