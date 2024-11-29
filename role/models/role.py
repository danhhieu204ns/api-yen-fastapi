from sqlalchemy import Column, String, Integer, text
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import TIMESTAMP
from configs.database import Base


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique = True)
    detail = Column(String, nullable=False)

    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

    user_account = relationship("UserRole", back_populates="role")