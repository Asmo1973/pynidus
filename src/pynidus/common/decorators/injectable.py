from pynidus.core.container import Container

def Injectable():
    """
    Decorator that marks a class as a provider and registers it with the global container.
    """
    def wrapper(cls):
        setattr(cls, "__is_injectable__", True)
        Container.get_instance().register(cls)
        return cls
    return wrapper
