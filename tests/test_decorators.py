from pynidus import Controller, Injectable, Module, Get, Post
from pynidus.core.module import ModuleMetadata

def test_injectable_decorator():
    @Injectable()
    class TestService:
        pass
    
    assert hasattr(TestService, "__is_injectable__")
    assert getattr(TestService, "__is_injectable__") is True

def test_controller_decorator():
    @Controller(prefix="/test")
    class TestController:
        pass
    
    assert hasattr(TestController, "__is_controller__")
    assert getattr(TestController, "__is_controller__") is True
    assert getattr(TestController, "__prefix__") == "/test"

def test_module_decorator():
    @Module(controllers=[], providers=[])
    class TestModule:
        pass
    
    assert hasattr(TestModule, "__module_metadata__")
    metadata = getattr(TestModule, "__module_metadata__")
    assert isinstance(metadata, ModuleMetadata)
    assert metadata.controllers == []
    assert metadata.providers == []

def test_http_decorators():
    class TestController:
        @Get("/get")
        def get_method(self):
            pass
        
        @Post("/post")
        def post_method(self):
            pass

    assert hasattr(TestController.get_method, "__route__")
    get_route = getattr(TestController.get_method, "__route__")
    assert get_route.path == "/get"
    assert get_route.method == "GET"

    assert hasattr(TestController.post_method, "__route__")
    post_route = getattr(TestController.post_method, "__route__")
    assert post_route.path == "/post"
    assert post_route.method == "POST"
