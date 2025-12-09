# Core Concepts

Pynidus is built around the concept of **Modules**. A module is a cohesive block of code that encapsulates a specific set of capabilities.

## Modules

A module is defined using the `@Module` decorator. It metadata defines the controllers and providers that belong to the module.

```python
from pynidus import Module

@Module(
    controllers=[CatController],
    providers=[CatService],
    imports=[DogModule] # Import other modules
)
class CatModule:
    pass
```

## Controllers

Controllers are responsible for handling incoming requests and returning responses to the client. They are defined using the `@Controller` decorator.

```python
from pynidus import Controller, Get, Post, Body

@Controller("/cats")
class CatController:
    def __init__(self, service: CatService):
        self.service = service

    @Get("/")
    def find_all(self):
        return self.service.find_all()

    @Post("/")
    def create(self, create_cat_dto: CreateCatDto):
        return self.service.create(create_cat_dto)
```

## Providers & Dependency Injection

Providers are plain Python classes that can be injected as dependencies. They are marked with `@Injectable()`.

```python
from pynidus import Injectable

@Injectable()
class CatService:
    def find_all(self):
        return ["Tabby", "Siamese"]
```

Pynidus automatically resolves dependencies based on type hints in the `__init__` method of your controllers and providers.

## Application Bootstrap

To start the application, use `NidusFactory`.

```python
from pynidus import NidusFactory

app = NidusFactory.create(AppModule)
```
