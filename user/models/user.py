from sqlalchemy import Boolean, Column, Integer, String, text, Date, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import TIMESTAMP
from configs.database import Base
from borrow.models.borrow import Borrow


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, nullable=False, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=True)
    full_name = Column(String, nullable=False)
    phone_number = Column(String, nullable=True)
    birthdate = Column(Date, nullable=True)
    address = Column(String, nullable=True)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

    auth_credential = relationship("AuthCredential", back_populates="user", uselist=False, passive_deletes=True)
    user_roles = relationship("UserRole", back_populates="user", passive_deletes=True)