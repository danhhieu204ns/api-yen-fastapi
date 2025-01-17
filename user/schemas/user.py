from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date
from auth_credential.schemas.auth_credential import AuthCredentialResponse
from role.schemas.role import RoleResponse


class UserBase(BaseModel):
    full_name: str
    email: Optional[str] = None
    phone_number: Optional[str] = None
    birthdate: Optional[date] = None
    address: Optional[str] = None


class UserCreate(UserBase):
    username: str
    password: str


class UserUpdate(UserBase):
    full_name: Optional[str] = None


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    auth_credential: AuthCredentialResponse
    
    class Config:
        from_attributes = True


class UserPageableResponse(BaseModel):
    users: list[UserResponse]

    total_pages: int
    total_data: int

    class Config:
        from_attributes = True
