from typing import List, Optional
from fastapi import Header, HTTPException

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
