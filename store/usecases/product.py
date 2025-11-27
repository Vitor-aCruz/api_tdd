from decimal import Decimal
from typing import List
from uuid import UUID
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
import pymongo
from store.core.exceptions import NotFoundException
from store.db.mongo import db_client
from store.schemas.product import ProductIn, ProductOut, ProductUpdate, ProductUpdateOut
from bson.decimal128 import Decimal128


class ProductUsecase:
    # ATENÇÃO AQUI: Adicione o parâmetro 'client' como opcional
    def __init__(self, client: AsyncIOMotorClient = None) -> None:
        # Se um client for passado (no teste), usa ele. Se não, usa o padrão (produção).
        self.client = client or db_client.get_client()
        self.database: AsyncIOMotorDatabase = self.client.get_database()
        self.collection = self.database.get_collection("products")

    async def create(self, body: ProductIn) -> ProductOut:
        # product_model = ProductModel(**body.model_dump())
        # await self.collection.insert_one(product_model.model_dump())
        # return ProductOut(**product_model.model_dump())

        data = body.model_dump()
        existing = await self.collection.find_one({"id": data["id"]})
        if existing:
            raise Exception("Product already exists")
        try:
            await self.collection.insert_one(data)
            return ProductOut(**data)
        except Exception as e:
            raise Exception(e)

    async def get(self, id: UUID) -> ProductOut:
        result = await self.collection.find_one({"id": id})
        if not result:
            raise NotFoundException(message=f"Product not found with filter: {id}")
        return ProductOut(**result)

    async def query(self) -> List[ProductOut]:
        docs = []
        cursor = self.collection.find()
        async for item in cursor:

            # Convert Decimal128 -> Decimal
            if isinstance(item.get("price"), Decimal128):
                item["price"] = item["price"].to_decimal()

            # Defaults
            if item.get("price") is None:
                item["price"] = Decimal("0")

            if item.get("status") is None:
                item["status"] = True

            docs.append(ProductOut(**item))

        return docs

    async def update(self, id: UUID, body: ProductUpdate) -> ProductUpdateOut:

        data = body.model_dump(exclude_none=True)

        # Fix: convert Decimal128 -> Decimal before creating the schema
        for k, v in data.items():
            if isinstance(v, Decimal128):
                data[k] = v.to_decimal()

        # Now build the validated schema
        ProductUpdate(**data)  # valida mas não guarda

        # Convert Decimal -> Decimal128 for DB
        update_data = {}
        for k, v in data.items():
            if isinstance(v, Decimal):
                update_data[k] = Decimal128(str(v))
            else:
                update_data[k] = v

        result = await self.collection.find_one_and_update(
            {"id": id},
            {"$set": update_data},
            return_document=pymongo.ReturnDocument.AFTER,
        )

        if not result:
            raise NotFoundException(message=f"Product not found with filter: {id}")

        # Convert result for output
        if isinstance(result.get("price"), Decimal128):
            result["price"] = result["price"].to_decimal()

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
