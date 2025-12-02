from typing import Callable, Any, Dict

# Global registry for event handlers
# Map: channel -> handler function
EVENT_HANDLERS: Dict[str, Callable] = {}

def EventPattern(pattern: str):
    """
    Decorator to register a method as an event handler for a specific pattern/channel.
    """
    def decorator(func: Callable):
        EVENT_HANDLERS[pattern] = func
        return func
    return decorator
