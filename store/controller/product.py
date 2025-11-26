from fastapi import APIRouter, Body, Depends, HTTPException, Path
from pydantic import UUID4


from store.core.exceptions import NotFoundException
from store.schemas.product import ProductIn, ProductOut
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


# parei em 21:51
