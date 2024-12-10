from datetime import date, datetime
from pydantic import BaseModel
from typing import Optional


class RolePermissionBase(BaseModel):
    name: str
    detail: str
    

class RolePermissionCreate(RolePermissionBase):
    pass


class RolePermissionUpdate(BaseModel):
    detail: str


class RolePermissionResponse(RolePermissionBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class RolePermissionPageableResponse(BaseModel):
    role_permissions: list[RolePermissionResponse]

    total_pages: int
    total_data: int

    class Config:
        from_attributes = True
