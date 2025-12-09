# Security

Pynidus allows you to secure your endpoints using Role-Based Access Control (RBAC) and OAuth2/JWT.

## Enabling OAuth2

First, install the security extras:

```bash
uv add "pynidus[security]"
```

Then configure your environment variables:

```ini
OAUTH2__ENABLED=true
OAUTH2__SECRET_KEY=your-secret-key
OAUTH2__ALGORITHM=HS256
OAUTH2__AUDIENCE=your-audience
OAUTH2__ISSUER=your-issuer
```

## Protecting Endpoints

Use the `@Security` decorator to restrict access to controllers or specific methods.

```python
from pynidus import Controller, Get, Security

@Controller("/admin")
@Security(["admin"]) # Requires "admin" role for all methods
class AdminController:
    
    @Get("/dashboard")
    def dashboard(self):
        return {"data": "secret"}

    @Get("/public")
    @Security([]) # Overrides class security (public access)
    def public(self):
        return {"data": "public"}
```

The `Security` decorator checks the JWT token (if enabled) in the `Authorization` header (`Bearer <token>`). It verifies the signature, expiration, audience, issuer, and checks if the `roles` claim contains the required role.
