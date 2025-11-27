from typing import List
from fastapi import APIRouter, Body, Depends, HTTPException, Path, status
from pydantic import UUID4


from store.core.exceptions import NotFoundException
from store.schemas.product import ProductIn, ProductOut, ProductUpdate
from store.usecases.product import ProductUsecase

router = APIRouter(tags=["products"])


def get_product_usecase() -> ProductUsecase:
    return ProductUsecase()


@router.post("/", status_code=201)
async def post_product(
    body: ProductIn = Body(...),
    usecase: ProductUsecase = Depends(get_product_usecase),
) -> ProductOut:
    return await usecase.create(body)


@router.get("/{id}", status_code=200)
async def get_products(
    id: UUID4 = Path(alias="id"),
    usecase: ProductUsecase = Depends(get_product_usecase),
) -> ProductOut:
    try:
        return await usecase.get(id)
    except NotFoundException as exc:
        raise HTTPException(status_code=404, detail=exc.message)


@router.get("/", status_code=200)
async def query(
    usecase: ProductUsecase = Depends(get_product_usecase),
) -> List[ProductOut]:
    return await usecase.query()


@router.patch("/{id}", status_code=200)
async def patch_product(
    id: UUID4 = Path(alias="id"),
    body: ProductUpdate = Body(...),
    usecase: ProductUsecase = Depends(get_product_usecase),
) -> ProductOut:
    return await usecase.update(id, body)


@router.delete("/{id}", status_code=204)
async def delete_product(
    id: UUID4 = Path(alias="id"),
    usecase: ProductUsecase = Depends(get_product_usecase),
) -> None:
    try:
        await usecase.delete(id=id)
    except NotFoundException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)
