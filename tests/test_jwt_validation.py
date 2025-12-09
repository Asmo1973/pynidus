import pytest
import os
from fastapi.testclient import TestClient
from pynidus import NidusFactory, Module, Controller, Get, Security, Injectable
from datetime import datetime, timedelta, timezone

try:
    from jose import jwt
except ImportError:
    jwt = None

# Mock keys
SECRET_KEY = "testsecret"
ALGORITHM = "HS256"
VALID_AUDIENCE = "test-audience"
VALID_ISSUER = "test-issuer"

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
    os.environ["OAUTH2__AUDIENCE"] = VALID_AUDIENCE
    os.environ["OAUTH2__ISSUER"] = VALID_ISSUER
    yield
    # Cleanup
    if "OAUTH2__ENABLED" in os.environ:
        del os.environ["OAUTH2__ENABLED"]
    if "OAUTH2__SECRET_KEY" in os.environ:
        del os.environ["OAUTH2__SECRET_KEY"]
    if "OAUTH2__ALGORITHM" in os.environ:
        del os.environ["OAUTH2__ALGORITHM"]
    if "OAUTH2__AUDIENCE" in os.environ:
        del os.environ["OAUTH2__AUDIENCE"]
    if "OAUTH2__ISSUER" in os.environ:
        del os.environ["OAUTH2__ISSUER"]

@pytest.fixture
def client(oauth2_env):
    if jwt is None:
        pytest.skip("python-jose not installed")
    app = NidusFactory.create(SecureModule)
    return TestClient(app)

def create_token(roles: list, audience=None, issuer=None):
    expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode = {"exp": expire, "roles": roles, "sub": "testuser"}
    if audience:
        to_encode["aud"] = audience
    if issuer:
        to_encode["iss"] = issuer
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def test_valid_token_with_audience_and_issuer(client):
    token = create_token(["admin"], audience=VALID_AUDIENCE, issuer=VALID_ISSUER)
    response = client.get("/secure", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    assert response.json() == {"message": "Top Secret"}

def test_invalid_audience(client):
    token = create_token(["admin"], audience="wrong-audience", issuer=VALID_ISSUER)
    response = client.get("/secure", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"

def test_invalid_issuer(client):
    token = create_token(["admin"], audience=VALID_AUDIENCE, issuer="wrong-issuer")
    response = client.get("/secure", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"

def test_missing_audience(client):
    # Config expects audience, token has none
    token = create_token(["admin"], issuer=VALID_ISSUER)
    response = client.get("/secure", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"

def test_missing_issuer(client):
    # Config expects issuer, token has none
    token = create_token(["admin"], audience=VALID_AUDIENCE)
    response = client.get("/secure", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"
