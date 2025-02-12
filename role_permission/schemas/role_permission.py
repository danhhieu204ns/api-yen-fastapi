from datetime import date, datetime
from pydantic import BaseModel
from typing import Optional

from permission.schemas.permission import PermissionResponse
from role.schemas.role import RoleResponse


class RolePermissionBase(BaseModel):
    id: Optional[int]
    role_id: int
    permission_id: int
    created_at: Optional[datetime]

    class Config:
        from_attributes = True
    

class RolePermissionCreate(BaseModel):
    role_id: int
    permission_id: int


class RolePermissionUpdate(BaseModel):
    role_id: int
    permission_id: int


class RolePermissionResponse(BaseModel):
    id: Optional[int]
    role: RoleResponse
    permission: PermissionResponse
    created_at: Optional[datetime]

    class Config:
        from_attributes = True


class ListRolePermissionResponse(BaseModel):
    role_permissions: list[RolePermissionResponse]
    tolal_data: int

    class Config:
        from_attributes = True


class RolePermissionPageableResponse(BaseModel):
    role_permissions: list[RolePermissionResponse]

    total_pages: int
    total_data: int

    class Config:
        from_attributes = True


class RolePermissionSearch(BaseModel):
    role_id: Optional[int]
    permission_id: Optional[int]

    class Config:
        from_attributes = True