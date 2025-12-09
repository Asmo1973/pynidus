from typing import List, Optional
from fastapi import Header, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
try:
    from jose import jwt, JWTError
except ImportError:
    jwt = None
    JWTError = None

from pynidus.core.config import OAuth2Config


class SecurityExpressionEvaluator:
    def __init__(self, roles: List[str]):
        self.roles = set(roles)

    def has_role(self, role: str) -> bool:
        return role in self.roles
    
    def has_any_role(self, *roles: str) -> bool:
        return any(r in self.roles for r in roles)

    def is_authenticated(self) -> bool:
        return True

    def evaluate(self, expression: str) -> bool:
        context = {
            "has_role": self.has_role,
            "has_any_role": self.has_any_role,
            "is_authenticated": self.is_authenticated
        }
        try:
            # Safe eval with restricted globals
            return bool(eval(expression, {"__builtins__": None}, context))
        except Exception:
            return False

class RoleChecker:
    def __init__(self, allowed_roles: List[str], pre_authorize: Optional[str] = None):
        self.allowed_roles = allowed_roles
        self.pre_authorize = pre_authorize

    def __call__(self, x_user_roles: Optional[str] = Header(default=None, alias="x-user-roles")):
        if not x_user_roles:
            raise HTTPException(status_code=403, detail="Missing role header")
        
        user_roles = [role.strip() for role in x_user_roles.split(",")]
        
        if self.pre_authorize:
            evaluator = SecurityExpressionEvaluator(user_roles)
            if not evaluator.evaluate(self.pre_authorize):
                raise HTTPException(status_code=403, detail="Insufficient permissions")
            return True

        # Legacy role check
        if self.allowed_roles and not any(role in self.allowed_roles for role in user_roles):
             raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        return True

class OAuth2RoleChecker:
    def __init__(self, allowed_roles: List[str], config: OAuth2Config, pre_authorize: Optional[str] = None):
        self.allowed_roles = allowed_roles
        self.config = config
        self.pre_authorize = pre_authorize
        self.oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)

    async def __call__(self, token: Optional[str] = Depends(OAuth2PasswordBearer(tokenUrl="token", auto_error=False))):
        if not self.config.enabled:
             raise HTTPException(status_code=500, detail="OAuth2 security is configured but disabled in settings")

        if not token:
            raise HTTPException(status_code=401, detail="Not authenticated")
            
        if jwt is None:
            raise ImportError("python-jose is required for OAuth2 security. Install 'pynidus[security]'")

        try:
            kwargs = {}
            options = {
                "verify_aud": False,
                "verify_iss": False
            }
            
            if self.config.audience:
                kwargs["audience"] = self.config.audience
                options["verify_aud"] = True
            
            if self.config.issuer:
                kwargs["issuer"] = self.config.issuer
                options["verify_iss"] = True

            payload = jwt.decode(token, self.config.secret_key, algorithms=[self.config.algorithm], options=options, **kwargs)
            
            if self.config.audience and "aud" not in payload:
                 raise HTTPException(status_code=401, detail="Invalid audience")
            
            user_roles = payload.get("roles", [])
            if isinstance(user_roles, str):
                user_roles = [r.strip() for r in user_roles.split(",")]
        except JWTError:
            raise HTTPException(status_code=401, detail="Could not validate credentials")

        if self.pre_authorize:
            evaluator = SecurityExpressionEvaluator(user_roles)
            if not evaluator.evaluate(self.pre_authorize):
                raise HTTPException(status_code=403, detail="Insufficient permissions")
            return True

        # Legacy role check
        if self.allowed_roles and not any(role in self.allowed_roles for role in user_roles):
            raise HTTPException(status_code=403, detail="Insufficient permissions")

        return True
