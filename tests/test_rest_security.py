import pytest
from fastapi.testclient import TestClient
from pynidus import NidusFactory, Module, Controller, Get, Security, Injectable

@Injectable()
class SecureService:
    def get_secret(self) -> str:
        return "Top Secret"

@Controller()
class SecureController:
    def __init__(self, service: SecureService):
        self.service = service

    @Get("/public")
    def public_endpoint(self):
        return {"message": "Public"}

    @Get("/secure")
    @Security(["admin"])
    def secure_endpoint(self):
        return {"message": self.service.get_secret()}

    @Get("/multi-role")
    @Security(["admin", "editor"])
    def multi_role_endpoint(self):
        return {"message": "Authorized"}

@Module(
    controllers=[SecureController],
    providers=[SecureService],
)
class SecureModule:
    pass

@pytest.fixture
def client():
    app = NidusFactory.create(SecureModule)
    return TestClient(app)

def test_public_endpoint(client):
    response = client.get("/public")
    assert response.status_code == 200
    assert response.json() == {"message": "Public"}

def test_secure_endpoint_no_header(client):
    response = client.get("/secure")
    assert response.status_code == 403
    assert response.json() == {"detail": "Missing role header"}

def test_secure_endpoint_wrong_role(client):
    response = client.get("/secure", headers={"x-user-roles": "user"})
    assert response.status_code == 403
    assert response.json() == {"detail": "Insufficient permissions"}

def test_secure_endpoint_correct_role(client):
    response = client.get("/secure", headers={"x-user-roles": "admin"})
    assert response.status_code == 200
    assert response.json() == {"message": "Top Secret"}

def test_multi_role_endpoint(client):
    # Admin should pass
    response = client.get("/multi-role", headers={"x-user-roles": "admin"})
    assert response.status_code == 200
    
    # Editor should pass
    response = client.get("/multi-role", headers={"x-user-roles": "editor"})
    assert response.status_code == 200
    
    # User should fail
    response = client.get("/multi-role", headers={"x-user-roles": "user"})
    assert response.status_code == 403

def test_multiple_roles_in_header(client):
    # User has both user and admin roles
    response = client.get("/secure", headers={"x-user-roles": "user,admin"})
    assert response.status_code == 200
