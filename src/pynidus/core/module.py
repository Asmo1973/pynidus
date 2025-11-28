from typing import List, Type, Any, Optional

class ModuleMetadata:
    def __init__(
        self,
        controllers: List[Type[Any]] = [],
        providers: List[Type[Any]] = [],
        imports: List[Type[Any]] = [],
        exports: List[Type[Any]] = [],
    ):
        self.controllers = controllers
        self.providers = providers
        self.imports = imports
        self.exports = exports

def Module(
    controllers: Optional[List[Type[Any]]] = None,
    providers: Optional[List[Type[Any]]] = None,
    imports: Optional[List[Type[Any]]] = None,
    exports: Optional[List[Type[Any]]] = None,
):
    """
    Decorator that marks a class as a module.
    """
    def wrapper(cls):
        metadata = ModuleMetadata(
            controllers=controllers or [],
            providers=providers or [],
            imports=imports or [],
            exports=exports or [],
        )
        setattr(cls, "__module_metadata__", metadata)
        return cls
    return wrapper
