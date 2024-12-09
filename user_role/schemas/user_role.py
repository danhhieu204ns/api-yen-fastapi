from datetime import date, datetime
from pydantic import BaseModel


class UserRoleBase(BaseModel):
    user_id: int
    role_id: int
    

class UserRoleCreate(UserRoleBase):
    pass


class UserRoleUpdate(UserRoleBase):
    pass


class UserRoleResponse(BaseModel):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class UserRolePageableResponse(BaseModel):
    user_roles: list[UserRoleResponse]
    total_pages: int
    total_data: int

    class Config:
        from_attributes = True
