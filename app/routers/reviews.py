from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db_depends import get_async_db

from app.schemas import Review as ReviewSchema, ReviewCreate
from app.models.reviews import Review as ReviewModel
from app.models.products import Product as ProductModel
from app.models.users import User as UserModel
from app.auth import get_current_user, get_current_admin, get_current_buyer

from app.services.review_service import update_product_rating


# Создаём маршрутизатор для товаров
router = APIRouter(
    prefix="/reviews",
    tags=["reviews"],
)


@router.get("/", response_model=list[ReviewSchema])
async def get_all_reviews(db: AsyncSession = Depends(get_async_db)):
    """
    Возвращает список всех отзывов.
    """
    result = await db.scalars(
        select(ReviewModel).join(ProductModel).where(ReviewModel.is_active == True, ProductModel.is_active == True))
    reviews = result.all()
    return reviews


@router.get("/{product_id}/reviews", response_model=list[ReviewSchema])
async def get_review(product_id: int, db: AsyncSession = Depends(get_async_db)):
    """
    Возвращает отзыв по ID товара.
    """
    # Проверяем, существует ли активный товар
    result = await db.scalars(
        select(ProductModel).where(ProductModel.id == product_id, ProductModel.is_active == True)
    )
    product = result.first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found or inactive")

    # Находим отзыв по ID товара
    result = await db.scalars(
        select(ReviewModel).join(ProductModel).where(ReviewModel.is_active == True,
                                                     ProductModel.id == product_id))
    reviews = result.all()
    if not reviews:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found or inactive")

    return reviews


@router.post("/", response_model=ReviewSchema, status_code=status.HTTP_201_CREATED)
async def create_review(
    review: ReviewCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: UserModel = Depends(get_current_buyer)
):
    """
    Создаёт новый отзыв, привязанный к текущему покупателю (только для 'buyer').
    """
    if review.grade < 1 or review.grade > 5:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Grade must be between 1 and 5")
    product_result = await db.scalars(
        select(ProductModel).where(ProductModel.id == review.product_id, ProductModel.is_active == True)
    )
    if not product_result.first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Product not found or inactive")
    db_review = ReviewModel(**review.model_dump(), user_id=current_user.id)
    db.add(db_review)
    await db.flush()
    await update_product_rating(db, review.product_id)
    await db.commit()
    await db.refresh(db_review)  # Для получения id и is_active из базы
    return db_review


@router.delete("/{review_id}", response_model=ReviewSchema)
async def delete_review(
    review_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: UserModel = Depends(get_current_admin)
):
    """
    Выполняет мягкое удаление отзыва (только для 'admin').
    """
    result = await db.scalars(
        select(ReviewModel).where(ReviewModel.id == review_id, ReviewModel.is_active == True)
    )
    review = result.first()
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found or inactive")
    await db.execute(
        update(ReviewModel).where(ReviewModel.id == review_id).values(is_active=False)
    )
    await update_product_rating(db, review.product_id)
    await db.commit()
    await db.refresh(review)  # Для возврата is_active = False
    return review