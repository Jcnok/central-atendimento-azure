from sqlalchemy import Column, Integer, String, Sequence
from sqlalchemy.orm import relationship
from src.config.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, Sequence('user_id_seq'), primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    chamados = relationship("Chamado", back_populates="user")
