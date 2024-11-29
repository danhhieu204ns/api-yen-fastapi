from datetime import date, datetime
from pydantic import BaseModel
from role.schemas.role import RoleResponse


class UserAccountBase(BaseModel):
    username: str
    active_user: bool


class UserAccountResponse(UserAccountBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class UserAccountResponseWithRole(UserAccountBase):
    id: int
    role: list[RoleResponse]
    created_at: datetime

    class Config:
        from_attributes = True


class UserAccountPageableResponse(BaseModel):
    user_accounts: list[UserAccountResponse]
    total_pages: int
    total_data: int

    class Config:
        from_attributes = True