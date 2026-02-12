from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.models.db import Base
from src.config import settings
from src.models.product_schema import ProductCreate, ProductUpdate
from src.services.products_service import (
    create_product,
    get_product,
    update_product,
    delete_product,
)


def get_test_db():
    # Use the same DB as the app inside docker-compose (productdb)
    engine = create_engine(
        settings.DATABASE_URL.unicode_string(),
        pool_pre_ping=True,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_create_and_get_product_unit():
    db_gen = get_test_db()
    db = next(db_gen)
    payload = ProductCreate(
        name="Unit Test Product",
        description="Unit test description",
        price=10.5,
        stock_quantity=5,
    )
    created = create_product(db, payload)
    fetched = get_product(db, created.id)
    assert fetched is not None
    assert fetched.name == "Unit Test Product"


def test_update_and_delete_product_unit():
    db_gen = get_test_db()
    db = next(db_gen)
    payload = ProductCreate(
        name="Unit Test Product 2",
        description="Unit test desc 2",
        price=15.0,
        stock_quantity=10,
    )
    created = create_product(db, payload)
    updated = update_product(
        db,
        created.id,
        ProductUpdate(price=20.0, stock_quantity=8),
    )
    assert updated.price == 20.0
    assert updated.stock_quantity == 8

    deleted = delete_product(db, created.id)
    assert deleted is True
    assert get_product(db, created.id) is None
