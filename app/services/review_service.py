from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.reviews import Review as ReviewModel
from app.models.products import Product as ProductModel


async def update_product_rating(db: AsyncSession, product_id: int) -> None:
    result = await db.execute(
        select(func.avg(ReviewModel.grade)).where(
            ReviewModel.product_id == product_id,
            ReviewModel.is_active.is_(True)
        )
    )
    avg_rating = result.scalar() or 0.0

    product = await db.get(ProductModel, product_id)
    if product is not None:
        product.rating = float(avg_rating)