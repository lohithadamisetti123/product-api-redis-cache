import time
import pytest
import httpx
import redis


API_BASE = "http://api-service:8080"
REDIS_HOST = "redis"
REDIS_PORT = 6379


@pytest.fixture(scope="session")
def redis_client():
    client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    for _ in range(30):
        try:
            if client.ping():
                return client
        except Exception:
            time.sleep(1)
    pytest.skip("Redis not available")


def test_create_and_get_product_cache_miss_then_hit(redis_client):
    payload = {
        "name": "Integration Product",
        "description": "Integration test product",
        "price": 25.5,
        "stock_quantity": 12,
    }
    with httpx.Client(base_url=API_BASE) as client:
        resp = client.post("/products", json=payload)
        assert resp.status_code == 201
        product = resp.json()
        product_id = product["id"]

        cache_key = f"product:{product_id}"
        redis_client.delete(cache_key)

        resp1 = client.get(f"/products/{product_id}")
        assert resp1.status_code == 200
        assert redis_client.get(cache_key) is not None

        resp2 = client.get(f"/products/{product_id}")
        assert resp2.status_code == 200


def test_update_invalidate_cache(redis_client):
    payload = {
        "name": "Integration Product 2",
        "description": "Integration test product 2",
        "price": 30.0,
        "stock_quantity": 20,
    }
    with httpx.Client(base_url=API_BASE) as client:
        resp = client.post("/products", json=payload)
        assert resp.status_code == 201
        product = resp.json()
        product_id = product["id"]

        cache_key = f"product:{product_id}"

        client.get(f"/products/{product_id}")
        assert redis_client.get(cache_key) is not None

        update_payload = {"price": 35.0}
        resp_upd = client.put(f"/products/{product_id}", json=update_payload)
        assert resp_upd.status_code == 200

        assert redis_client.get(cache_key) is None


def test_delete_invalidate_and_404(redis_client):
    payload = {
        "name": "Integration Product 3",
        "description": "Integration test product 3",
        "price": 40.0,
        "stock_quantity": 5,
    }
    with httpx.Client(base_url=API_BASE) as client:
        resp = client.post("/products", json=payload)
        assert resp.status_code == 201
        product = resp.json()
        product_id = product["id"]
        cache_key = f"product:{product_id}"

        client.get(f"/products/{product_id}")
        assert redis_client.get(cache_key) is not None

        resp_del = client.delete(f"/products/{product_id}")
        assert resp_del.status_code == 204

        assert redis_client.get(cache_key) is None

        resp_get = client.get(f"/products/{product_id}")
        assert resp_get.status_code == 404
