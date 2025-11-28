from fastapi import FastAPI, APIRouter
from typing import Type, Any, Dict, List
import inspect
from pynidus.core.module import ModuleMetadata
from pynidus.common.decorators.http import RouteDefinition

class NidusFactory:
    @staticmethod
    def create(app_module: Type[Any]) -> FastAPI:
        app = FastAPI()
        factory = NidusFactory()
        factory.initialize(app, app_module)
        return app

    def __init__(self):
        self.container: Dict[Type[Any], Any] = {}

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
        if provider_cls in self.container:
            return

        # Resolve dependencies for the provider
        init_signature = inspect.signature(provider_cls.__init__)
        dependencies = []
        
        for param_name, param in init_signature.parameters.items():
            if param_name == 'self':
                continue
            
            # Ignore *args and **kwargs
            if param.kind in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD):
                continue

            if param.annotation == inspect.Parameter.empty:
                 raise ValueError(f"Dependency {param_name} in {provider_cls.__name__} must have a type hint.")
            
            # Recursively ensure dependency is registered (if it's a provider)
            # In a real app, we'd check if it's in the module's providers or imports.
            # For simplicity, we assume global registration or self-contained for now.
            if param.annotation not in self.container:
                 # Auto-register if not explicitly registered? 
                 # Or throw error? Let's try to instantiate if possible.
                 self.register_provider(param.annotation)
            
            dependencies.append(self.container[param.annotation])

        instance = provider_cls(*dependencies)
        self.container[provider_cls] = instance

    def register_controller(self, app: FastAPI, controller_cls: Type[Any]):
        # Resolve dependencies
        init_signature = inspect.signature(controller_cls.__init__)
        dependencies = []
        
        for param_name, param in init_signature.parameters.items():
            if param_name == 'self':
                continue
            
            # Ignore *args and **kwargs
            if param.kind in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD):
                continue

            if param.annotation == inspect.Parameter.empty:
                 raise ValueError(f"Dependency {param_name} in {controller_cls.__name__} must have a type hint.")
            
            if param.annotation not in self.container:
                # Try to register it if it's missing (simple auto-wiring)
                self.register_provider(param.annotation)
            
            dependencies.append(self.container[param.annotation])

        controller_instance = controller_cls(*dependencies)
        
        # Register Routes
        prefix = getattr(controller_cls, "__prefix__", "")
        router = APIRouter(prefix=prefix)

        for name, method in inspect.getmembers(controller_instance, predicate=inspect.ismethod):
            if hasattr(method, "__route__"):
                route_def: RouteDefinition = getattr(method, "__route__")
                
                # We need to wrap the method to ensure FastAPI calls it correctly
                # FastAPI expects the function signature to match the parameters.
                # Since we are using a bound method, 'self' is already handled.
                
                router.add_api_route(
                    route_def.path,
                    method,
                    methods=[route_def.method],
                )
        
        app.include_router(router)
