from typing import List
from uuid import UUID
import pytest
from store.core.exceptions import ProductAlreadyExistsError
from store.schemas.product import ProductIn, ProductOut, ProductUpdateOut


@pytest.mark.asyncio
async def test_usecase_create_should_return_success(product_usecase, product_in):
    # 'product_usecase' aqui é a fixture do conftest
    result = await product_usecase.create(body=product_in)

    assert isinstance(result, ProductOut)
    assert result.name == "Iphone 14 Pro Max"


@pytest.mark.asyncio
async def test_usecase_create_should_return_raise(product_usecase, products_inserted):
    body = ProductIn(name="Iphone 11 Pro Max", quantity=50, price="7.500", status=True)

    with pytest.raises(ProductAlreadyExistsError):
        await product_usecase.create(body=body)


@pytest.mark.asyncio
async def test_usecase_get_should_return_success(product_inserted, product_usecase):
    result = await product_usecase.get(id=product_inserted.id)

    assert isinstance(result, ProductOut)
    assert result.name == "Iphone 14 Pro Max"


async def test_usecase_get_should_return_not_found(product_usecase):
    with pytest.raises(Exception) as err:
        await product_usecase.get(id=UUID("123e4367-e89b-42d3-a456-426614174000"))
    assert (
        err.value.args[0]
        == "Product not found with filter: 123e4367-e89b-42d3-a456-426614174000"
    )


@pytest.mark.usefixtures("products_inserted")
async def test_usecase_query_should_return_success(product_usecase, products_inserted):
    result = await product_usecase.query()

    assert isinstance(result, List)
    assert len(result) > 1


async def test_usecase_update_should_return_success(
    product_inserted, product_up, product_usecase
):
    product_up.price = "7.500"
    result = await product_usecase.update(id=product_inserted.id, body=product_up)

    assert isinstance(result, ProductUpdateOut)


async def test_usecase_delete_should_return_success(product_inserted, product_usecase):
    result = await product_usecase.delete(id=product_inserted.id)
    assert result is True


async def test_usecase_delete_should_not_found(product_usecase):
    with pytest.raises(Exception) as err:
        await product_usecase.delete(id=UUID("123e4367-e89b-42d3-a456-426614174000"))
    assert (
        err.value.args[0]
        == "Product not found with filter: 123e4367-e89b-42d3-a456-426614174000"
    )
