from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from src.api import products
from src.models.db import Base, engine, get_db
from src.services.products_service import seed_products_if_empty
from src.config import settings

app = FastAPI(title="Product API with Redis Caching")


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    db_gen = get_db()
    db: Session = next(db_gen)
    try:
        seed_products_if_empty(db)
    finally:
        db.close()


@app.get("/health")
def health():
    return {"status": "ok"}


app.include_router(products.router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("src.main:app", host="0.0.0.0", port=settings.API_PORT, reload=False)
