from datetime import date, datetime
from pydantic import BaseModel
from user_account.schemas.user_account import UserAccountResponse
from role.schemas.role import RoleResponse


class UserRoleBase(BaseModel):
    user_account_id: int
    role_id: int
    

class UserRoleCreate(UserRoleBase):
    pass


class UserRoleUpdate(UserRoleBase):
    pass


class UserRoleResponse(BaseModel):
    id: int
    created_at: datetime
    user_account: UserAccountResponse
    role: RoleResponse

    class Config:
        from_attributes = True


class ListUserRoleResponse(BaseModel):
    id: int
    created_at: datetime
    user_account: UserAccountResponse
    role: list[RoleResponse]

    class Config:
        from_attributes = True


class UserRolePageableResponse(BaseModel):
    user_roles: list[UserRoleResponse]
    total_pages: int
    total_data: int

    class Config:
        from_attributes = True


class UserRoleImport(BaseModel):
    user_roles: list[UserRoleCreate]

    class Config:
        from_attributes = True
