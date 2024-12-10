from datetime import date, datetime
from pydantic import BaseModel
from typing import Optional


class PermissionBase(BaseModel):
    name: str
    detail: str
    

class PermissionCreate(PermissionBase):
    pass


class PermissionUpdate(PermissionBase):
    detail: str


class PermissionResponse(PermissionBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class PermissionPageableResponse(BaseModel):
    permissions: list[PermissionBase]

    total_pages: int
    total_data: int

    class Config:
        from_attributes = True
