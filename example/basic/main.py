from pynidus import NidusFactory, Module, Controller, Injectable, Get
import uvicorn

@Injectable()
class AppService:
    def get_hello(self) -> str:
        return "Hello World from Pynidus!"

@Controller()
class AppController:
    def __init__(self, app_service: AppService):
        self.app_service = app_service

    @Get("/")
    def get_hello(self):
        return {"message": self.app_service.get_hello()}

@Module(
    controllers=[AppController],
    providers=[AppService],
)
class AppModule:
    pass

def bootstrap():
    app = NidusFactory.create(AppModule)
    uvicorn.run(app, host="0.0.0.0", port=3000)

if __name__ == "__main__":
    bootstrap()
