from typing import List, Callable, Any

def Security(roles: List[str]):
    """
    Decorator to enforce role-based access control on a controller method.
    """
    def wrapper(func: Callable[..., Any]):
        setattr(func, "__security_roles__", roles)
        return func
    return wrapper
