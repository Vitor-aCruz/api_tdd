from typing import List
from uuid import UUID
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
import pymongo
from store.core.exceptions import NotFoundException
from store.db.mongo import db_client
from store.models.product import ProductModel
from store.schemas.product import ProductIn, ProductOut, ProductUpdate, ProductUpdateOut


class ProductUsecase:
    # ATENÇÃO AQUI: Adicione o parâmetro 'client' como opcional
    def __init__(self, client: AsyncIOMotorClient = None) -> None:
        # Se um client for passado (no teste), usa ele. Se não, usa o padrão (produção).
        self.client = client or db_client.get_client()
        self.database: AsyncIOMotorDatabase = self.client.get_database()
        self.collection = self.database.get_collection("products")

    async def create(self, body: ProductIn) -> ProductOut:
        product_model = ProductModel(**body.model_dump())
        await self.collection.insert_one(product_model.model_dump())
        return ProductOut(**product_model.model_dump())

    async def get(self, id: UUID) -> ProductOut:
        result = await self.collection.find_one({"id": id})
        if not result:
            raise NotFoundException(message=f"Product not found with filter: {id}")
        return ProductOut(**result)

    async def query(self) -> List[ProductOut]:
        return [ProductOut(**item) async for item in self.collection.find()]

    async def update(self, id: UUID, body: ProductUpdate) -> ProductUpdateOut:
        result = await self.collection.find_one_and_update(
            {"id": id},
            {"$set": body.model_dump(exclude_none=True)},
            return_document=pymongo.ReturnDocument.AFTER,
        )
        if not result:
            raise NotFoundException(message=f"Product not found with filter: {id}")
        return ProductUpdateOut(**result)

    async def delete(self, id: UUID):
        result = await self.collection.find_one({"id": id})
        # Verifica se o produto existe antes de tentar deletar
        if not result:
            raise NotFoundException(message=f"Product not found with filter: {id}")

        result = await self.collection.delete_one({"id": id})
        # Retorna True se algum documento foi deletado, caso contrário False
        return True if result.deleted_count > 0 else False


# Instância padrão para uso na aplicação (fora dos testes)
product_usecase = ProductUsecase()
