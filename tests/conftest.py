from uuid import UUID
import pytest
import pytest_asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from store.schemas.product import ProductIn, ProductUpdate
from store.usecases.product import ProductUsecase
from tests.schemas.factories import product_data, products_data
from httpx import AsyncClient


@pytest.fixture(scope="function")
def mongo_client():
    client = AsyncIOMotorClient(
        "mongodb://localhost:27017/store-tdd", uuidRepresentation="standard"
    )
    yield client
    client.close()


@pytest_asyncio.fixture(autouse=True)
async def clear_collections(mongo_client):
    yield
    # Usamos o mongo_client criado nesta sessão de teste, que está vivo
    collection_names = await mongo_client.get_database(
        "store"
    ).list_collection_names()  # Especifique o nome do banco se necessário
    for collection_name in collection_names:
        if collection_name.startswith("system"):
            continue
        await mongo_client.get_database("store")[collection_name].delete_many({})


@pytest.fixture
async def client() -> AsyncClient:
    from store.main import app

    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def product_id() -> UUID:
    return UUID("123e4567-e89b-42d3-a456-426614174000")


@pytest.fixture
def product_in(product_id):
    return ProductIn(**product_data(), id=product_id)


@pytest.fixture
def product_usecase(mongo_client):
    # AQUI ESTÁ O SEGREDO: Injetamos o cliente criado no teste dentro do Usecase
    return ProductUsecase(client=mongo_client)


@pytest.fixture
def product_up(product_id):
    return ProductUpdate(**product_data(), id=product_id)


@pytest.fixture
async def product_inserted(product_in, product_usecase):
    return await product_usecase.create(
        body=product_in
    )  # Cria o produto no banco para os testes que precisam dele


@pytest.fixture
def products_in():
    return [ProductIn(**product) for product in products_data()]


@pytest.fixture
async def products_inserted(products_in, product_usecase):
    return [await product_usecase.create(body=product_in) for product_in in products_in]


# Terminei no Crud 15:35
