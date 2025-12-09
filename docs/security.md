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

## Spring-Style Expressions (@PreAuthorize)

For more complex security logic, you can use the `@PreAuthorize` decorator, which supports expression checking similar to Spring Security.

```python
from pynidus import Controller, Get, PreAuthorize

@Controller("/secure")
class SecureController:
    
    @Get("/admin")
    @PreAuthorize("has_role('admin')")
    def admin_only(self):
        return {"msg": "Admin only"}

    @Get("/complex")
    @PreAuthorize("has_role('admin') or has_role('manager')")
    def admin_or_manager(self):
        return {"msg": "Admin or Manager"}
        
    @Get("/authenticated")
    @PreAuthorize("is_authenticated()")
    def just_authenticated(self):
        return {"msg": "Authenticated"}
```

### Supported Functions

- `has_role('role_name')`: Returns True if the user has the specified role.
- `has_any_role('role1', 'role2', ...)`: Returns True if the user has any of the specified roles.
- `is_authenticated()`: Returns True if a valid token is present.
