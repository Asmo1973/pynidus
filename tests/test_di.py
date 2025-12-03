import pytest
from pynidus.core.container import Container
from pynidus.common.decorators.injectable import Injectable

@Injectable()
class ServiceA:
    def get_value(self):
        return "A"

@Injectable()
class ServiceB:
    def __init__(self, service_a: ServiceA):
        self.service_a = service_a

    def get_value(self):
        return f"B-{self.service_a.get_value()}"

class ServiceC:
    pass

def test_container_singleton():
    container = Container()
    
    # Resolve twice
    instance1 = container.resolve(ServiceA)
    instance2 = container.resolve(ServiceA)
    
    assert instance1 is instance2
    assert instance1.get_value() == "A"

def test_container_dependency_injection():
    container = Container()
    
    service_b = container.resolve(ServiceB)
    
    assert isinstance(service_b, ServiceB)
    assert isinstance(service_b.service_a, ServiceA)
    assert service_b.get_value() == "B-A"

def test_container_auto_register():
    container = Container()
    
    # ServiceC is not decorated but should be auto-registered/resolved
    instance = container.resolve(ServiceC)
    assert isinstance(instance, ServiceC)
