from pydantic import BaseModel, Field, ConfigDict, EmailStr, HttpUrl
from decimal import Decimal
from enum import Enum
from datetime import datetime


class CategoryCreate(BaseModel):
    """
    Модель для создания и обновления категории.
    Используется в POST и PUT запросах.
    """
    name: str = Field(..., min_length=3, max_length=50,
                      description="Название категории (3-50 символов)")
    parent_id: int | None = Field(None, description="ID родительской категории, если есть")


class Category(BaseModel):
    """
    Модель для ответа с данными категории.
    Используется в GET-запросах.
    """
    id: int = Field(..., description="Уникальный идентификатор категории")
    name: str = Field(..., description="Название категории")
    parent_id: int | None = Field(None, description="ID родительской категории, если есть")
    is_active: bool = Field(..., description="Активность категории")

    model_config = ConfigDict(from_attributes=True)


class ProductCreate(BaseModel):
    """
    Модель для создания и обновления товара.
    Используется в POST и PUT запросах.
    """
    name: str = Field(..., min_length=3, max_length=100,
                      description="Название товара (3-100 символов)")
    description: str | None = Field(None, max_length=500,
                                       description="Описание товара (до 500 символов)")
    price: Decimal = Field(..., gt=0, description="Цена товара (больше 0)", decimal_places=2)
    image_url: str | None = Field(None, description="URL изображения товара")
    stock: int = Field(..., ge=0, description="Количество товара на складе (0 или больше)")
    category_id: int = Field(..., description="ID категории, к которой относится товар")


class Product(BaseModel):
    """
    Модель для ответа с данными товара.
    Используется в GET-запросах.
    """
    id: int = Field(..., description="Уникальный идентификатор товара")
    name: str = Field(..., description="Название товара")
    description: str | None = Field(None, description="Описание товара")
    price: Decimal = Field(..., description="Цена товара в рублях", gt=0, decimal_places=2)
    image_url: str | None = Field(None, description="URL изображения товара")
    stock: int = Field(..., description="Количество товара на складе")
    category_id: int = Field(..., description="ID категории")
    seller_id: int = Field(..., description="ID продавца")
    is_active: bool = Field(..., description="Активность товара")
    rating: float = Field(..., description="Рейтинг товара")
    created_at: datetime = Field(..., description="Дата создания")

    model_config = ConfigDict(from_attributes=True)

class UserRole(str, Enum):
    """
    Тип данных для поля role.
    Используется в модели UserCreate.
    """
    buyer = "buyer"
    seller = "seller"
    admin = "admin"

class UserCreate(BaseModel):
    """
    Модель для создания и обновления пользователя.
    Используется в POST и PUT запросах.
    """
    email: EmailStr = Field(description="Email пользователя")
    password: str = Field(min_length=8, description="Пароль (минимум 8 символов)")
    role: UserRole = Field(default=UserRole.buyer, description="Роль пользователя")


class User(BaseModel):
    """
    Модель для ответа с данными пользователя.
    Используется в GET-запросах.
    """
    id: int = Field(..., description="Уникальный идентификатор пользователя")
    email: EmailStr = Field(..., description="Email пользователя")
    is_active: bool = Field(..., description="Активность пользователя")
    role: UserRole = Field(default=UserRole.buyer, description="Роль пользователя")
    model_config = ConfigDict(from_attributes=True)


class RefreshTokenRequest(BaseModel):
    """
    Модель передачи Refresh токена
    """
    refresh_token: str = Field(..., description="Refresh token")


class ReviewCreate(BaseModel):
    """
    Модель для создания и обновления отзыва.
    Используется в POST и PUT запросах.
    """
    product_id: int = Field(..., description="ID товара, к которому относится отзыв")
    comment: str | None = Field(None, max_length=1000, description="Текст отзыва")
    grade: int = Field(..., ge=1, le=5, description="Оценка товара от 1 до 5")


class Review(BaseModel):
    """
    Модель для ответа с данными отзыва.
    Используется в GET-запросах.
    """
    id: int = Field(..., description="Уникальный идентификатор отзыва")
    user_id: int = Field(..., description="ID пользователя, оставившего отзыв")
    product_id: int = Field(..., description="ID товара, к которому относится отзыв")
    comment: str | None = Field(None, description="Текст отзыва")
    comment_date: datetime = Field(..., description="Дата и время создания отзыва")
    grade: int = Field(..., ge=1, le=5, description="Оценка товара от 1 до 5")
    is_active: bool = Field(..., description="Активность отзыва")

    model_config = ConfigDict(from_attributes=True)


class ProductList(BaseModel):
    """
    Список пагинации для товаров.
    """
    items: list[Product] = Field(description="Товары для текущей страницы")
    total: int = Field(ge=0, description="Общее количество товаров")
    page: int = Field(ge=1, description="Номер текущей страницы")
    page_size: int = Field(ge=1, description="Количество элементов на странице")

    model_config = ConfigDict(from_attributes=True)  # Для чтения из ORM-объектов
