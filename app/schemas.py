from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime, date


class Token(BaseModel):
    access_token: str
    token_type: str

class Tokendata(BaseModel):
    id: Optional[int] = None


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str
    date_of_birth: Optional[date] = None
    address: Optional[str] = None
    phone_number: Optional[str] = None

class UserUpdate(BaseModel):
    name: str
    date_of_birth: Optional[date] = None
    address: Optional[str] = None
    phone_number: Optional[str] = None

class UserRePwd(BaseModel):
    password: str

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    name: str
    created_at: datetime
    
    class Config:
        from_attributes = True


