from uuid import UUID
import pytest
import pytest_asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from store.controller.product import get_product_usecase
from store.schemas.product import ProductIn, ProductUpdate
from store.usecases.product import ProductUsecase
from tests.schemas.factories import product_data, products_data
from httpx import ASGITransport, AsyncClient
from store.main import app


# ----------------------------------------------------------------------------
# ✔️ CLIENTE MONGO PARA TESTES (ÚNICA VERSÃO CORRETA)
# ----------------------------------------------------------------------------
@pytest.fixture
async def mongo_client():
    client = AsyncIOMotorClient(
        "mongodb://localhost:27017/store-tdd-tests",
        uuidRepresentation="standard",  # ⭐ importante
    )

    db = client.get_database()
    await db["products"].delete_many({})  # limpa antes dos testes

    yield client
    client.close()


# ----------------------------------------------------------------------------
# ✔️ LIMPA COLEÇÕES DEPOIS DE CADA TESTE
# ----------------------------------------------------------------------------
@pytest_asyncio.fixture(autouse=True)
async def clear_collections(mongo_client):
    yield
    db = mongo_client.get_database()
    collections = await db.list_collection_names()
    for collection in collections:
        if not collection.startswith("system"):
            await db[collection].delete_many({})


# ----------------------------------------------------------------------------
# FIXTURES DE DADOS
# ----------------------------------------------------------------------------
@pytest.fixture
def products_url() -> str:
    return "/products/"


@pytest.fixture
def product_id() -> UUID:
    return UUID("123e4567-e89b-42d3-a456-426614174000")


@pytest.fixture
def product_in(product_id):
    return ProductIn(**product_data(), id=product_id)


@pytest.fixture
def product_usecase(mongo_client):
    return ProductUsecase(client=mongo_client)


@pytest.fixture
def product_up(product_id):
    return ProductUpdate(**product_data(), id=product_id)


@pytest.fixture
async def product_inserted(product_in, product_usecase):
    return await product_usecase.create(body=product_in)


@pytest.fixture
def products_in():
    return [ProductIn(**product) for product in products_data()]


@pytest.fixture
async def products_inserted(products_in, product_usecase):
    return [await product_usecase.create(body=p) for p in products_in]


# ----------------------------------------------------------------------------
# ✔️ CLIENTE DE TESTES FASTAPI (COMPATÍVEL COM HTTPX NOVO)
# ----------------------------------------------------------------------------
@pytest.fixture
async def client(mongo_client):
    async def override_usecase():
        return ProductUsecase(client=mongo_client)

    app.dependency_overrides[get_product_usecase] = override_usecase

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c

    app.dependency_overrides.clear()
