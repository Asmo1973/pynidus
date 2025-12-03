from typing import Type, TypeVar, Dict, Any, Optional

T = TypeVar("T")

class Container:
    _instance: Optional["Container"] = None

    def __init__(self):
        self._providers: Dict[Type, Any] = {}
        self._instances: Dict[Type, Any] = {}

    @classmethod
    def get_instance(cls) -> "Container":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def register(self, cls: Type[T], instance: Optional[T] = None) -> None:
        """
        Register a class. If instance is provided, it's treated as a singleton.
        """
        self._providers[cls] = cls
        if instance:
            self._instances[cls] = instance

    def resolve(self, cls: Type[T]) -> T:
        """
        Resolve a class instance. Currently supports singleton scope.
        """
        if cls in self._instances:
            return self._instances[cls]

        if cls not in self._providers:
            # Auto-register if not explicitly registered (simple behavior)
            self._providers[cls] = cls

        # Simple instantiation (no constructor injection yet for simplicity, 
        # or we can add basic recursive resolution)
        # Let's try basic recursive resolution
        
        try:
            init_params = cls.__init__.__annotations__
        except AttributeError:
            init_params = {}

        dependencies = {}
        for param_name, param_type in init_params.items():
            if param_name == 'return':
                continue
            # Check if param_type is a class we can resolve
            if isinstance(param_type, type):
                dependencies[param_name] = self.resolve(param_type)

        instance = cls(**dependencies)
        self._instances[cls] = instance
        return instance
