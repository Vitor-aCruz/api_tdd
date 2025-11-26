from fastapi import APIRouter

from store.controller.product import router as product

api_router = APIRouter()

api_router.include_router(product, prefix="/products")
