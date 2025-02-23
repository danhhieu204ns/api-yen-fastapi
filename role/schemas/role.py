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


class ListRoleResponse(BaseModel):
    roles: list[RoleResponse]
    total_data: int

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


class RoleSearch(BaseModel):
    name: Optional[str] = None
    detail: Optional[str] = None

    class Config:
        from_attributes = True


class RoleNameResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class ListRoleNameResponse(BaseModel):
    roles: list[RoleNameResponse]
    total_data: int

    class Config:
        from_attributes = True
        