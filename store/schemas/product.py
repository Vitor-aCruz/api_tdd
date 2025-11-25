from decimal import Decimal
from typing import Annotated, Optional
from bson import Decimal128
from pydantic import AfterValidator, BaseModel, Field
from store.schemas.base import BaseSchemaMixin, OutSchema


class ProductBase(BaseModel):
    name: str = Field(..., description="Name of the product", max_length=100)
    quantity: int = Field(..., description="Quantity of the product in stock")
    price: float = Field(..., description="Price of the product")
    status: bool = Field(..., description="Status of the product")


class ProductIn(ProductBase, BaseSchemaMixin):
    pass


class ProductOut(ProductIn, OutSchema):
    pass


def convert_decimal_128(v):
    return Decimal128(str(v))


Decimal_ = Annotated[Decimal, AfterValidator(convert_decimal_128)]


class ProductUpdate(ProductBase):
    quantity: Optional[int] = Field(
        None, description="Quantity of the product in stock"
    )
    price: Optional[float] = Field(None, description="Price of the product")
    status: Optional[bool] = Field(None, description="Status of the product")


class ProductUpdateOut(ProductUpdate):
    pass
