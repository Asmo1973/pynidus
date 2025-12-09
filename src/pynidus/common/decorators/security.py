from typing import List, Callable, Any

def Security(roles: List[str]):
    """
    Decorator to enforce role-based access control on a controller method.
    Legacy support alias for simple role checks.
    """
    def wrapper(func: Callable[..., Any]):
        setattr(func, "__security_roles__", roles)
        return func
    return wrapper

def PreAuthorize(condition: str):
    """
    Spring Security-style decorator to enforce access control using expressions.
    Example: @PreAuthorize("has_role('admin') or has_role('manager')")
    """
    def wrapper(func: Callable[..., Any]):
        setattr(func, "__security_pre_authorize__", condition)
        return func
    return wrapper
