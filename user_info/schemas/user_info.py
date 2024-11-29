from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date
from user_account.schemas.user_account import UserAccountResponse
from role.schemas.role import RoleResponse


class UserInfoBase(BaseModel):
    name: str
    birthdate: date
    address: str
    phone_number: str


class UserCreate(BaseModel):
    name: str
    birthdate: Optional[date] = None
    address: Optional[str] = None
    phone_number: Optional[str] = None
    username: str
    password: str


class UserInfoUpdate(BaseModel):
    name: Optional[str] = None
    birthdate: Optional[date] = None
    address: Optional[str] = None
    phone_number: Optional[str] = None


class UserInfoResponse(UserInfoBase):
    id: int
    created_at: datetime

    user_account: UserAccountResponse
    
    class Config:
        from_attributes = True


class UserInfoPageableResponse(BaseModel):
    users: list[UserInfoResponse]

    total_pages: int
    total_data: int

    class Config:
        from_attributes = True


class UserInfoImport(BaseModel):
    user_infos: list[UserCreate]