from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel


class UserResponse(BaseModel):
    id: int
    full_name: str
    
    class Config:
        from_attributes = True


class RoleResponse(BaseModel):
    id: int
    name: str
    detail: str

    class Config:
        from_attributes = True


class UserRoleBase(BaseModel):
    user_id: int
    role_id: int
    

class UserRoleCreate(UserRoleBase):
    pass


class UserRoleUpdate(UserRoleBase):
    pass


class UserRoleResponse(BaseModel):
    id: int
    user: UserResponse
    role: RoleResponse

    created_at: datetime

    class Config:
        from_attributes = True


class ListUserRoleResponse(BaseModel):
    user_roles: list[UserRoleResponse]
    total_data: int

    class Config:
        from_attributes = True


class UserRolePageableResponse(BaseModel):
    user_roles: list[UserRoleResponse]
    total_pages: int
    total_data: int

    class Config:
        from_attributes = True
