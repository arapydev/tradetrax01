from pydantic import BaseModel

# Schema base con los campos comunes
class AccountBase(BaseModel):
    name: str
    broker: str
    account_number: str
    balance: float
    api_key: str
    api_secret: str
    is_active: bool = True

# Schema para la creación de una cuenta (lo que la API recibe)
class AccountCreate(AccountBase):
    pass

# Schema para la respuesta de la API (lo que la API devuelve)
class Account(AccountBase):
    id: int

    class ConfigDict:
        orm_mode = True