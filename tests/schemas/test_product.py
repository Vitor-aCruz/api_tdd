from uuid import UUID

import pytest
from store.schemas.product import ProductIn
from tests.schemas.factories import product_data


@pytest.mark.asyncio
async def test_schemas_return_success():
    data = product_data()
    product = ProductIn.model_validate(data)

    assert product.name == "Iphone 14 Pro Max"
    assert isinstance(product.id, UUID)


@pytest.mark.asyncio
async def test_schemas_return_raise():
    data = {"name": "Iphone 14 Pro Max", "quantity": 10, "price": 8500}

    with pytest.raises(Exception) as err:
        ProductIn(**data)

    assert err.value.errors()[0] == {
        "type": "missing",
        "loc": ("status",),
        "msg": "Field required",
        "input": {"name": "Iphone 14 Pro Max", "quantity": 10, "price": 8500.0},
        "url": "https://errors.pydantic.dev/2.12/v/missing",
    }
