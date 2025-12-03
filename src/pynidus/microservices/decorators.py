from typing import Callable, Any, Dict

# Global registry for event handlers (Legacy/Simple mode)
# Map: channel -> handler function
# We keep this for backward compatibility or simple function handlers
EVENT_HANDLERS: Dict[str, Callable] = {}

def EventPattern(pattern: str):
    """
    Decorator to register a method as an event handler for a specific pattern/channel.
    """
    def decorator(func: Callable):
        # Store metadata on the function itself for scanning
        setattr(func, "_event_pattern", pattern)
        
        # Also register in global if it's a standalone function (not method)
        # It's hard to distinguish at decoration time, but we can try.
        # For now, we populate EVENT_HANDLERS too, but Listener will prefer Controller scanning.
        EVENT_HANDLERS[pattern] = func
        return func
    return decorator
