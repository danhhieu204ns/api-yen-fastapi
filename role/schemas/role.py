from datetime import date, datetime
from pydantic import BaseModel
from typing import Optional


class RoleBase(BaseModel):
    name: str
    detail: str
    

class RoleCreate(RoleBase):
    pass


class RoleUpdate(BaseModel):
    detail: str


class RoleResponse(RoleBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class RolePageableResponse(BaseModel):
    roles: list[RoleResponse]

    total_pages: int
    total_data: int

    class Config:
        from_attributes = True


class RoleImport(BaseModel):
    roles: list[RoleCreate]

    class Config:
        from_attributes = True
        