from fastapi import Form
from pydantic import BaseModel
from typing import Optional


# Token
class Token(BaseModel):
    access_token: str
    token_type: str


class Tokendata(BaseModel):
    id: Optional[int] = None