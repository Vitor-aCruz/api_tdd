from uuid import UUID
import pytest
import pytest_asyncio
from store.db.mongo import db_client
from store.schemas.product import ProductIn
from tests.schemas.factories import product_data


@pytest.fixture
def mongo_client():
    return db_client.get_client()


@pytest_asyncio.fixture
async def clear_collections():

    collections = await db_client.list_collection_names()

    for name in collections:
        if name.startswith("system."):
            continue
        await db_client[name].delete_many({})


@pytest.fixture
def product_id() -> UUID:
    return UUID("123e4567-e89b-42d3-a456-426614174000")


@pytest.fixture
def product_in(product_id):
    return ProductIn(**product_data(), id=product_id)
