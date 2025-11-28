
def Controller(prefix: str = ""):
    """
    Decorator that marks a class as a controller.
    """
    def wrapper(cls):
        setattr(cls, "__is_controller__", True)
        setattr(cls, "__prefix__", prefix)
        return cls
    return wrapper
