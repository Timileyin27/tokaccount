from pydantic import BaseModel, EmailStr, Field, model_validator
from typing import List, Optional,Literal

class Token(BaseModel):
    access_token: str
    token_type: str
class TokenData(BaseModel):
    id: int 
class UserCreate (BaseModel):
    email:EmailStr
    password:str  = Field(min_length=8, max_length=64)
    confirm_password:str = Field(min_length=8, max_length=64)
    @model_validator(mode="after")
    def passwords_match(self):
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match")
        return self
class UserOut (BaseModel):
    id:int
    email: EmailStr
    model_config= {
        "from_attributes": True
    }

class AccountType(BaseModel):
    name : str
    price: float
    amount_in_stock: int
    amount_sold: int
    owner_id: int

class AccountOut(BaseModel):
    id: int
    price: float
    name : str
    amount_in_stock: int
    amount_sold: int
    owner_id: int
    model_config= {
        "from_attributes": True
    }