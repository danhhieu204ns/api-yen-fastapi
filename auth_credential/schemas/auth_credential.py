from datetime import date, datetime
from pydantic import BaseModel


class AuthCredentialResponse(BaseModel):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class AuthCredentialPageableResponse(BaseModel):
    auth_credentials: list[AuthCredentialResponse]

    total_pages: int
    total_data: int

    class Config:
        from_attributes = True
