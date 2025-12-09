import pytest
import os
from fastapi.testclient import TestClient
from pynidus import NidusFactory, Module, Controller, Get, Security, Injectable
from datetime import datetime, timedelta
try:
    from jose import jwt
except ImportError:
    jwt = None

# Mock keys
SECRET_KEY = "testsecret"
ALGORITHM = "HS256"

@Injectable()
class SecureService:
    def get_secret(self) -> str:
        return "Top Secret"

@Controller()
class SecureController:
    def __init__(self, service: SecureService):
        self.service = service

    @Get("/secure")
    @Security(["admin"])
    def secure_endpoint(self):
        return {"message": self.service.get_secret()}

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
    expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode = {"exp": expire, "roles": roles, "sub": "testuser"}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def test_secure_endpoint_no_token(client):
    response = client.get("/secure")
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}

def test_secure_endpoint_valid_token_admin(client):
    token = create_token(["admin"])
    response = client.get("/secure", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json() == {"message": "Top Secret"}

def test_secure_endpoint_valid_token_user(client):
    token = create_token(["user"])
    # Should fail because admin is required
    response = client.get("/secure", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403
    assert response.json() == {"detail": "Insufficient permissions"}

def test_secure_endpoint_invalid_token(client):
    response = client.get("/secure", headers={"Authorization": "Bearer invalidtoken"})
    assert response.status_code == 401
