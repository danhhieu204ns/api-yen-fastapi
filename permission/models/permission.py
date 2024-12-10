from sqlalchemy import Column, String, Integer, text
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import TIMESTAMP
from configs.database import Base


class Permission(Base):
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique = True)
    detail = Column(String, nullable=False)

    granted_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

    role_permissions = relationship("RolePermission", back_populates="permission", passive_deletes=True)
    