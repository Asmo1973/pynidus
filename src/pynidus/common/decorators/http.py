from typing import Callable, Any, Optional

class RouteDefinition:
    def __init__(self, path: str, method: str):
        self.path = path
        self.method = method

def Get(path: str = "/"):
    def wrapper(func: Callable[..., Any]):
        setattr(func, "__route__", RouteDefinition(path, "GET"))
        return func
    return wrapper

def Post(path: str = "/"):
    def wrapper(func: Callable[..., Any]):
        setattr(func, "__route__", RouteDefinition(path, "POST"))
        return func
    return wrapper

def Put(path: str = "/"):
    def wrapper(func: Callable[..., Any]):
        setattr(func, "__route__", RouteDefinition(path, "PUT"))
        return func
    return wrapper

def Delete(path: str = "/"):
    def wrapper(func: Callable[..., Any]):
        setattr(func, "__route__", RouteDefinition(path, "DELETE"))
        return func
    return wrapper

def Patch(path: str = "/"):
    def wrapper(func: Callable[..., Any]):
        setattr(func, "__route__", RouteDefinition(path, "PATCH"))
        return func
    return wrapper
