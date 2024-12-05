from sqlalchemy import Column, Integer, String, text, Date, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import TIMESTAMP
from configs.database import Base
from borrow.models.borrow import Borrow


class UserInfo(Base):
    __tablename__ = "user_infos"

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    birthdate = Column(Date, nullable=True)
    address = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

    user_account_id = Column(Integer, ForeignKey("user_accounts.id", ondelete="CASCADE"), nullable=False)

    user_account = relationship("UserAccount", back_populates="user_info")
    borrows = relationship("Borrow", back_populates="user", foreign_keys=[Borrow.user_id], passive_deletes=True)