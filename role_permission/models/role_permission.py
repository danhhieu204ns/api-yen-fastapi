from sqlalchemy import Column, ForeignKey, String, Integer, text
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import TIMESTAMP
from configs.database import Base


class RolePermission (Base):
    __tablename__ = "role_permissions"

    id = Column(Integer, primary_key=True, index=True)
    role_id = Column(Integer, ForeignKey('roles.id', ondelete='CASCADE'), nullable=False)
    permission_id = Column(Integer, ForeignKey('permissions.id', ondelete='CASCADE'), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

    role = relationship("Role", back_populates="role_permissions", passive_deletes=True)
    permission = relationship("Permission", back_populates="role_permissions", passive_deletes=True)
    