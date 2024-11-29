from sqlalchemy import Column, ForeignKey, Integer, text
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import TIMESTAMP
from configs.database import Base


class UserRole(Base):
    __tablename__ = "user_roles"

    id = Column(Integer, primary_key=True, index=True)

    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

    user_account_id = Column(Integer, ForeignKey("user_accounts.id"), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)

    user_account = relationship("UserAccount", back_populates="role")
    role = relationship("Role", back_populates="user_account")