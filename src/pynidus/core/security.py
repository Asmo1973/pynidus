from typing import List, Optional
from fastapi import Header, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
try:
    from jose import jwt, JWTError
except ImportError:
    jwt = None
    JWTError = None

from pynidus.core.config import OAuth2Config

class RoleChecker:
    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, x_user_roles: Optional[str] = Header(default=None, alias="x-user-roles")):
        if not x_user_roles:
            raise HTTPException(status_code=403, detail="Missing role header")
        
        user_roles = [role.strip() for role in x_user_roles.split(",")]
        
        # Check if any of the user's roles match the allowed roles
        if not any(role in self.allowed_roles for role in user_roles):
             raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        return True

class OAuth2RoleChecker:
    def __init__(self, allowed_roles: List[str], config: OAuth2Config):
        self.allowed_roles = allowed_roles
        self.config = config
        self.oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)

    async def __call__(self, token: Optional[str] = Depends(OAuth2PasswordBearer(tokenUrl="token", auto_error=False))):
        if not self.config.enabled:
             # Fallback or error? If this checker is used, it interprets enabled=False as "feature disabled"
             # but we shouldn't be using this checker if it's disabled. 
             # However, for safety:
             raise HTTPException(status_code=500, detail="OAuth2 security is configured but disabled in settings")

        if not token:
            raise HTTPException(status_code=401, detail="Not authenticated")
            
        if jwt is None:
            raise ImportError("python-jose is required for OAuth2 security. Install 'pynidus[security]'")

        try:
            payload = jwt.decode(token, self.config.secret_key, algorithms=[self.config.algorithm])
            user_roles = payload.get("roles", [])
            # Support both list and comma-separated string
            if isinstance(user_roles, str):
                user_roles = [r.strip() for r in user_roles.split(",")]
        except JWTError:
            raise HTTPException(status_code=401, detail="Could not validate credentials")

        if not any(role in self.allowed_roles for role in user_roles):
            raise HTTPException(status_code=403, detail="Insufficient permissions")

        return True
