from shop.repository import Repository

def test_repository_saves_and_loads_catalog(tmp_path):
    data_path = tmp_path / "data"
    data_path.mkdir()
    catalog_path = data_path / "catalog.json"

    data = {
        "products": [
            {
                "id": "P001",
                "type": "piece",
                "name": "Кружка",
                "category": "merch",
                "price": 590,
                "stock": 10
            }
        ]
    }

    with open(catalog_path, "w", encoding="utf-8") as f:
        import json
        json.dump(data, f, ensure_ascii=False, indent=2)

    repo = Repository(data_path)
    products = repo.load_catalog()
    assert "P001" in products

    product = products["P001"]
    product.consume_stock(5)

    assert product.stock == 5

def test_repository_creates_empty_orders_if_missing(tmp_path):
    data_path = tmp_path / "data"
    data_path.mkdir()
    repo = Repository(data_path)
    data = repo.load_orders()
    assert "cart" in data
    assert "orders" in data
    assert "next_order_id" in data
