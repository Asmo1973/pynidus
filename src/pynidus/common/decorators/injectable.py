
def Injectable():
    """
    Decorator that marks a class as a provider.
    """
    def wrapper(cls):
        # We can add metadata here if needed
        setattr(cls, "__is_injectable__", True)
        return cls
    return wrapper
