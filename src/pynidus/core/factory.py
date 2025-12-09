from fastapi import FastAPI, APIRouter, Depends
from typing import Type, Any, Dict, List
import inspect
from pydantic import BaseModel
import punq
import uvicorn

from pynidus.core.module import ModuleMetadata
from pynidus.common.decorators.http import RouteDefinition
from pynidus.core.security import RoleChecker, OAuth2RoleChecker
from pynidus.core.config import BaseSettings


class NidusFactory:
    @staticmethod
    def create(app_module: Type[Any]) -> FastAPI:
        app = FastAPI()
        factory = NidusFactory()
        factory.initialize(app, app_module)
        return app

    @staticmethod
    def listen(app_module: Type[Any], **kwargs):
        """
        Creates the application and starts the uvicorn server based on configuration.
        """
        app = NidusFactory.create(app_module)
        
        # We need to retrieve the container to get settings
        # This is a bit tricky since create() doesn't return the factory instance
        # Ideally, we should refactor create() or store the factory/container on the app state
        # For now, let's re-instantiate or assume standardized DI access.
        
        # Better approach: NidusFactory.create creates the container. 
        # But we don't return it.
        # Let's update create() to attach container to app.state
        pass 
        # Wait, I cannot change create() easily without breaking compatibility?
        # Let's inspect how to get the container. 
        # Actually, NidusFactory instance is local to create().
        
        # Alternative: Re-instantiate settings just for the server config
        # This is safe because settings are stateless/env-based
        settings = BaseSettings()
        
        # Override with kwargs
        host = kwargs.get("host", settings.server.host)
        port = kwargs.get("port", settings.server.port)
        ssl_keyfile = kwargs.get("ssl_keyfile", settings.server.ssl_keyfile)
        ssl_certfile = kwargs.get("ssl_certfile", settings.server.ssl_certfile)

        uvicorn.run(
            app, 
            host=host, 
            port=port, 
            ssl_keyfile=ssl_keyfile, 
            ssl_certfile=ssl_certfile
        )

    def __init__(self):
        self.container = punq.Container()

    def initialize(self, app: FastAPI, module_cls: Type[Any]):
        if not hasattr(module_cls, "__module_metadata__"):
            raise ValueError(f"{module_cls.__name__} is not a valid Module. Did you forget the @Module decorator?")
        
        metadata: ModuleMetadata = getattr(module_cls, "__module_metadata__")
        
        # 1. Process Imports (Recursion)
        for imported_module in metadata.imports:
            self.initialize(app, imported_module)

        # 2. Register Providers
        for provider_cls in metadata.providers:
            self.register_provider(provider_cls)

        # 3. Register Controllers
        for controller_cls in metadata.controllers:
            self.register_controller(app, controller_cls)

    def register_provider(self, provider_cls: Type[Any]):
        # Special handling for Pydantic models (Settings)
        if issubclass(provider_cls, BaseModel):
            try:
                self.container.resolve(provider_cls)
            except punq.MissingDependencyError:
                 instance = provider_cls()
                 self.container.register(provider_cls, instance=instance)
            return

        # Restore strict type hint validation
        init_signature = inspect.signature(provider_cls.__init__)
        for param_name, param in init_signature.parameters.items():
            if param_name == 'self':
                continue
            if param.kind in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD):
                continue
            if param.annotation == inspect.Parameter.empty:
                 raise ValueError(f"Dependency {param_name} in {provider_cls.__name__} must have a type hint.")

        # Explicitly register the class as both service and implementation
        self.container.register(provider_cls, provider_cls)

    def register_controller(self, app: FastAPI, controller_cls: Type[Any]):
        # Restore strict type hint validation for controllers too
        init_signature = inspect.signature(controller_cls.__init__)
        for param_name, param in init_signature.parameters.items():
            if param_name == 'self':
                continue
            if param.kind in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD):
                continue
            if param.annotation == inspect.Parameter.empty:
                 raise ValueError(f"Dependency {param_name} in {controller_cls.__name__} must have a type hint.")

        # Register the controller itself so punq can resolve it
        self.container.register(controller_cls, controller_cls)

        try:
            controller_instance = self.container.resolve(controller_cls)
        except punq.MissingDependencyError as e:
             # Fallback or better error message?
             # Punq error is usually descriptive enough but we can wrap it
             raise ValueError(f"Could not resolve dependencies for {controller_cls.__name__}: {e}")
        
        # Register Routes
        prefix = getattr(controller_cls, "__prefix__", "")
        router = APIRouter(prefix=prefix)

        for name, method in inspect.getmembers(controller_instance, predicate=inspect.ismethod):
            if hasattr(method, "__route__"):
                route_def: RouteDefinition = getattr(method, "__route__")
                
                route_dependencies = []
                
                if hasattr(method, "__security_roles__") or hasattr(method, "__security_pre_authorize__"):
                    roles = getattr(method, "__security_roles__", [])
                    pre_authorize = getattr(method, "__security_pre_authorize__", None)
                    
                    # Determine security mechanism
                    try:
                        settings = self.container.resolve(BaseSettings)
                    except punq.MissingDependencyError:
                         # Attempt to load BaseSettings if not explicitly registered
                         # This might happen if ConfigModule wasn't imported
                         settings = BaseSettings()

                    if settings.oauth2.enabled:
                        route_dependencies.append(Depends(OAuth2RoleChecker(roles, settings.oauth2, pre_authorize=pre_authorize)))
                    else:
                        route_dependencies.append(Depends(RoleChecker(roles, pre_authorize=pre_authorize)))


                router.add_api_route(
                    route_def.path,
                    method,
                    methods=[route_def.method],
                    dependencies=route_dependencies
                )
        
        app.include_router(router)
