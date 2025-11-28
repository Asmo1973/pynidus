from fastapi.testclient import TestClient
from pynidus import NidusFactory, Module, Controller, Injectable, Get

def test_integration_hello_world():
    @Injectable()
    class AppService:
        def get_hello(self) -> str:
            return "Hello Test!"

    @Controller()
    class AppController:
        def __init__(self, app_service: AppService):
            self.app_service = app_service

        @Get("/hello")
        def get_hello(self):
            return {"message": self.app_service.get_hello()}

    @Module(
        controllers=[AppController],
        providers=[AppService],
    )
    class AppModule:
        pass

    app = NidusFactory.create(AppModule)
    client = TestClient(app)

    response = client.get("/hello")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello Test!"}
