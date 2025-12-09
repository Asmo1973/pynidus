import pytest
import os
from fastapi.testclient import TestClient
from pynidus import NidusFactory, Module, Controller, Get, Injectable, PreAuthorize
from datetime import datetime, timedelta, timezone

try:
    from jose import jwt
except ImportError:
    jwt = None

# Mock keys
SECRET_KEY = "testsecret"
ALGORITHM = "HS256"

@Injectable()
class SecureService:
    def get_msg(self) -> str:
        return "Access Granted"

@Controller()
class SecureController:
    def __init__(self, service: SecureService):
        self.service = service

    @Get("/admin")
    @PreAuthorize("has_role('admin')")
    def admin_endpoint(self):
        return {"message": self.service.get_msg()}

    @Get("/any")
    @PreAuthorize("has_role('user') or has_role('admin')")
    def any_endpoint(self):
        return {"message": self.service.get_msg()}

    @Get("/auth")
    @PreAuthorize("is_authenticated()")
    def auth_endpoint(self):
        return {"message": self.service.get_msg()}
    
    @Get("/complex")
    @PreAuthorize("(has_role('a') and has_role('b')) or has_role('c')")
    def complex_endpoint(self):
        return {"message": self.service.get_msg()}

@Module(
    controllers=[SecureController],
    providers=[SecureService],
)
class SecureModule:
    pass

@pytest.fixture
def oauth2_env():
    # Enable OAuth2 via env vars
    os.environ["OAUTH2__ENABLED"] = "true"
    os.environ["OAUTH2__SECRET_KEY"] = SECRET_KEY
    os.environ["OAUTH2__ALGORITHM"] = ALGORITHM
    yield
    # Cleanup
    if "OAUTH2__ENABLED" in os.environ:
        del os.environ["OAUTH2__ENABLED"]
    if "OAUTH2__SECRET_KEY" in os.environ:
        del os.environ["OAUTH2__SECRET_KEY"]
    if "OAUTH2__ALGORITHM" in os.environ:
        del os.environ["OAUTH2__ALGORITHM"]

@pytest.fixture
def client(oauth2_env):
    if jwt is None:
        pytest.skip("python-jose not installed")
    app = NidusFactory.create(SecureModule)
    return TestClient(app)

def create_token(roles: list):
    expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode = {"exp": expire, "roles": roles, "sub": "testuser"}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def test_has_role_success(client):
    token = create_token(["admin"])
    response = client.get("/admin", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200

def test_has_role_fail(client):
    token = create_token(["user"])
    response = client.get("/admin", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403

def test_or_expression_success(client):
    token = create_token(["user"])
    response = client.get("/any", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200

def test_or_expression_success_2(client):
    token = create_token(["admin"])
    response = client.get("/any", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200

def test_is_authenticated(client):
    token = create_token([])
    response = client.get("/auth", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200

def test_complex_expression(client):
    # (a and b) or c
    
    # Just A -> basic fail
    token = create_token(["a"])
    assert client.get("/complex", headers={"Authorization": f"Bearer {token}"}).status_code == 403
    
    # A and B -> Pass
    token = create_token(["a", "b"])
    assert client.get("/complex", headers={"Authorization": f"Bearer {token}"}).status_code == 200
    
    # Just C -> Pass
    token = create_token(["c"])
    assert client.get("/complex", headers={"Authorization": f"Bearer {token}"}).status_code == 200
