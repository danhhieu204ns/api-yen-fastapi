from sqlalchemy import Column, Integer, String, Boolean, text
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import TIMESTAMP
from configs.database import Base


class UserAccount(Base):
    __tablename__ = 'user_accounts'
    
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    active_user = Column(Boolean, default=False)

    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

    user_info = relationship("UserInfo", back_populates="user_account")
    role = relationship("UserRole", back_populates="user_account")
