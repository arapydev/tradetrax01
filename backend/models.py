from sqlalchemy import Column, Integer, String, Float, Boolean
from .database import Base

class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    broker = Column(String, nullable=False)
    account_number = Column(String, nullable=False, unique=True)
    balance = Column(Float, nullable=False)
    api_key = Column(String, nullable=False) # Guardaremos esto encriptado más adelante
    api_secret = Column(String, nullable=False) # Igual que la api_key
    is_active = Column(Boolean, default=True)