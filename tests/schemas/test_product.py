from uuid import UUID
from store.schemas.product import ProductIn


def test_schemas_validated():

    data = {"name": "Iphone 14 Pro Max", "quantity": 10, "price": 8.500, "status": True}
    product = ProductIn(**data)

    assert product.name == "Iphone 14 Pro Max"
    assert isinstance(product.id, UUID)
