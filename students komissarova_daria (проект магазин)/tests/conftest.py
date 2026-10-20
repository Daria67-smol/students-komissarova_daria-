import pytest
import tempfile
import shutil
from pathlib import Path
from shop.repository import Repository
from shop.service import ShopService

@pytest.fixture
def tmp_data_dir():
    tmp_dir = Path(tempfile.mkdtemp())
    yield tmp_dir
    shutil.rmtree(tmp_dir)

@pytest.fixture
def sample_catalog(tmp_data_dir):
    catalog_path = tmp_data_dir / "catalog.json"
    data = {
        "products": [
            {"id": "P001", "type": "piece", "name": "Кружка", "category": "merch", "price": 590, "stock": 10},
            {"id": "P010", "type": "weight", "name": "Чай", "category": "tea", "price_per_kg": 2400, "min_kg": 0.1, "stock_kg": 5.0},
            {"id": "P020", "type": "digital", "name": "Курс", "category": "courses", "price": 1990},
        ]
    }
    with open(catalog_path, "w", encoding="utf-8") as f:
        import json
        json.dump(data, f, ensure_ascii=False, indent=2)
    return catalog_path

@pytest.fixture
def sample_promos(tmp_data_dir):
    promos_path = tmp_data_dir / "promos.json"
    data = {
        "promos": [
            {"code": "SALE10", "type": "percent", "percent": 10},
            {"code": "MINUS500", "type": "fixed", "amount": 500, "min_total": 3000},
        ]
    }
    with open(promos_path, "w", encoding="utf-8") as f:
        import json
        json.dump(data, f, ensure_ascii=False, indent=2)
    return promos_path

@pytest.fixture
def shop_service(tmp_data_dir, sample_catalog, sample_promos):
    # Создаём пустой orders.json
    orders_path = tmp_data_dir / "orders.json"
    with open(orders_path, "w", encoding="utf-8") as f:
        import json
        json.dump({"cart": {"items": [], "promo": None}, "orders": [], "next_order_id": 1}, f, ensure_ascii=False, indent=2)
    repo = Repository(tmp_data_dir)
    service = ShopService(repo=repo, log_path=tmp_data_dir / "shop.log")
    return service
