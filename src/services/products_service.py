from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import select
from src.models.product_model import Product
from src.models.product_schema import ProductCreate, ProductUpdate, ProductOut
from src.services.cache_service import (
    get_product_from_cache,
    set_product_in_cache,
    invalidate_product_cache,
)
from src.config import settings


def create_product(db: Session, payload: ProductCreate) -> ProductOut:
    product = Product(
        name=payload.name,
        description=payload.description,
        price=payload.price,
        stock_quantity=payload.stock_quantity,
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    invalidate_product_cache(product.id)
    return ProductOut.model_validate(product)


def get_product(db: Session, product_id: str) -> Optional[ProductOut]:
    cached = get_product_from_cache(product_id)
    if cached:
        return cached

    stmt = select(Product).where(Product.id == product_id)
    result = db.execute(stmt).scalar_one_or_none()
    if result is None:
        return None

    product_out = ProductOut.model_validate(result)
    set_product_in_cache(product_out, settings.CACHE_TTL_SECONDS)
    return product_out


def update_product(
    db: Session, product_id: str, payload: ProductUpdate
) -> Optional[ProductOut]:
    stmt = select(Product).where(Product.id == product_id)
    result = db.execute(stmt).scalar_one_or_none()
    if result is None:
        return None

    if payload.name is not None:
        result.name = payload.name
    if payload.description is not None:
        result.description = payload.description
    if payload.price is not None:
        result.price = payload.price
    if payload.stock_quantity is not None:
        result.stock_quantity = payload.stock_quantity

    db.add(result)
    db.commit()
    db.refresh(result)

    invalidate_product_cache(product_id)
    return ProductOut.model_validate(result)


def delete_product(db: Session, product_id: str) -> bool:
    stmt = select(Product).where(Product.id == product_id)
    result = db.execute(stmt).scalar_one_or_none()
    if result is None:
        return False
    db.delete(result)
    db.commit()
    invalidate_product_cache(product_id)
    return True


def seed_products_if_empty(db: Session) -> None:
    stmt = select(Product)
    existing: List[Product] = list(db.execute(stmt).scalars())
    if existing:
        return

    sample_payloads = [
        Product(
            name="Sample Product A",
            description="Seed product A",
            price=19.99,
            stock_quantity=50,
        ),
        Product(
            name="Sample Product B",
            description="Seed product B",
            price=29.99,
            stock_quantity=30,
        ),
        Product(
            name="Sample Product C",
            description="Seed product C",
            price=39.99,
            stock_quantity=10,
        ),
    ]
    db.add_all(sample_payloads)
    db.commit()
