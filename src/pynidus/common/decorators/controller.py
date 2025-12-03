from pynidus.core.container import Container

def Controller(prefix: str = ""):
    """
    Decorator that marks a class as a controller and registers it with the global container.
    """
    def wrapper(cls):
        setattr(cls, "__is_controller__", True)
        setattr(cls, "__prefix__", prefix)
        Container.get_instance().register(cls)
        return cls
    return wrapper
