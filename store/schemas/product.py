from pydantic import Field
from store.schemas.base import BaseSchemaMixin


class ProductIn(BaseSchemaMixin):
    name: str = Field(..., description="Name of the product", max_length=100)
    quantity: int = Field(..., description="Quantity of the product in stock")
    price: float = Field(..., description="Price of the product")
    status: bool = Field(..., description="Status of the product")


class ProductOut(ProductIn):
    pass
