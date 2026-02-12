from pydantic import BaseModel, Field, conint, confloat
from typing import Optional


class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1)
    price: confloat(gt=0)
    stock_quantity: conint(ge=0)


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, min_length=1)
    price: Optional[confloat(gt=0)] = None
    stock_quantity: Optional[conint(ge=0)] = None


class ProductOut(ProductBase):
    id: str

    class Config:
        from_attributes = True
