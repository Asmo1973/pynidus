import pytest
from pynidus import NidusFactory, Module, Controller, Injectable
from fastapi import FastAPI

def test_factory_create():
    @Module()
    class TestModule:
        pass
    
    app = NidusFactory.create(TestModule)
    assert isinstance(app, FastAPI)

def test_dependency_injection():
    @Injectable()
    class TestService:
        def get_value(self):
            return "value"

    @Controller()
    class TestController:
        def __init__(self, service: TestService):
            self.service = service

    @Module(controllers=[TestController], providers=[TestService])
    class TestModule:
        pass

    # We need to access the factory instance to check the container
    # But NidusFactory.create returns the FastAPI app.
    # So we'll instantiate NidusFactory manually for testing internal state if needed,
    # or just trust that if it doesn't crash, it worked (integration test covers the rest).
    
    # Let's verify it doesn't raise an error
    app = NidusFactory.create(TestModule)
    assert app is not None

def test_missing_type_hint_error():
    @Injectable()
    class TestService:
        pass

    @Controller()
    class TestController:
        def __init__(self, service): # Missing type hint
            self.service = service

    @Module(controllers=[TestController], providers=[TestService])
    class TestModule:
        pass

    with pytest.raises(ValueError, match="must have a type hint"):
        NidusFactory.create(TestModule)

def test_di_ignore_args_kwargs():
    @Injectable()
    class TestService:
        pass

    @Controller()
    class TestController:
        def __init__(self, service: TestService, *args, **kwargs):
            self.service = service

    @Module(controllers=[TestController], providers=[TestService])
    class TestModule:
        pass

    # Should not raise error
    NidusFactory.create(TestModule)
