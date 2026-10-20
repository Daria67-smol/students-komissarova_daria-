import json
from pathlib import Path
from typing import Any, Dict, List
from decimal import Decimal

from shop.products import Product, PieceProduct, WeightProduct, DigitalProduct
from shop.cart import CartItem
from shop.exceptions import InvalidPromoError


class Repository:
    def __init__(self, data_path: Path):
        self.data_path = data_path
        self.catalog_path = data_path / "catalog.json"
        self.promos_path = data_path / "promos.json"
        self.orders_path = data_path / "orders.json"

    def load_catalog(self) -> Dict[str, Product]:
        if not self.catalog_path.exists():
            raise FileNotFoundError("catalog.json не найден.")

        try:
            with open(self.catalog_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"catalog.json повреждён: {e}")

        products: Dict[str, Product] = {}
        raw_products = data.get("products", [])

        for p in raw_products:
            ptype = p["type"]
            pid = p["id"]
            name = p["name"]
            category = p["category"]

            if ptype == "piece":
                price = Decimal(str(p["price"]))
                stock = int(p["stock"])
                products[pid] = PieceProduct(pid, name, category, price, stock)

            elif ptype == "weight":
                price_val = p.get("price_per_kg") or p.get("price")
                if price_val is None:
                    raise ValueError(f"У весового товара {pid} не указана цена")

                products[pid] = WeightProduct(
                    pid,
                    name,
                    category,
                    Decimal(str(price_val)),
                    float(p.get("min_kg", 0.1)),
                    float(p.get("stock_kg", 0.0)),
                )

            elif ptype == "digital":
                products[pid] = DigitalProduct(
                    pid,
                    name,
                    category,
                    Decimal(str(p["price"])),
                )
            else:
                raise ValueError(f"Неизвестный тип товара: {ptype}")

        return products

    def load_promos(self) -> Dict[str, Any]:
        if not self.promos_path.exists():
            return {}

        try:
            with open(self.promos_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"promos.json повреждён: {e}")

        promos: Dict[str, Any] = {}
        from shop.discounts import create_discount

        for promo in data.get("promos", []):
            code = promo["code"]
            try:
                promos[code] = create_discount(code, promo)
            except InvalidPromoError as e:
                raise InvalidPromoError(f"Ошибка промокода {code}: {e}") from e
            except Exception as e:
                raise RuntimeError(f"Неожиданная ошибка при загрузке промокода {code}: {e}") from e

        return promos

    def load_orders(self) -> Dict[str, Any]:
        """Загружает состояние заказов и корзины. Возвращает структуру, готовую для использования в ShopService."""
        if not self.orders_path.exists():
            initial_data = {
                "cart": {"items": [], "promo": None},
                "orders": [],
                "next_order_id": 1,
            }
            self.save_orders(initial_data)
            return initial_data

        try:
            with open(self.orders_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"orders.json повреждён: {e}")

        cart_data = data.get("cart", {})
        cart_items: List[CartItem] = []
        for item in cart_data.get("items", []):
            qty_dec = Decimal(str(item["qty"]))
            cart_items.append(CartItem(product_id=item["product_id"], qty=qty_dec))

        data["cart"]["items"] = cart_items
        return data

    def save_orders(self, data: Dict[str, Any]) -> None:
        """Сохраняет заказы и корзину. data['cart']['items'] — список CartItem."""
        cart_items_raw = []
        for item in data["cart"].get("items", []):
            if isinstance(item, CartItem):
                qty_val = str(item.qty)
                cart_items_raw.append({
                    "product_id": item.product_id,
                    "qty": qty_val,
                })
            elif isinstance(item, dict):
                qty_val = str(item["qty"])
                cart_items_raw.append({
                    "product_id": item["product_id"],
                    "qty": qty_val,
                })

        save_data = {
            "cart": {
                "items": cart_items_raw,
                "promo": data["cart"].get("promo"),
            },
            "orders": data.get("orders", []),
            "next_order_id": data.get("next_order_id", 1),
        }

        with open(self.orders_path, "w", encoding="utf-8") as f:
            json.dump(save_data, f, ensure_ascii=False, indent=2)

    def save_catalog(self, products: Dict[str, Product]) -> None:
        items = []
        for pid in products.values():
            if isinstance(pid, PieceProduct):
                items.append({
                    "id": pid.id,
                    "type": "piece",
                    "name": pid.name,
                    "category": pid.category,
                    "price": str(pid.price),
                    "stock": pid.stock,
                })
            elif isinstance(pid, WeightProduct):
                items.append({
                    "id": pid.id,
                    "type": "weight",
                    "name": pid.name,
                    "category": pid.category,
                    "price_per_kg": str(pid.price),
                    "min_kg": float(pid.min_kg),
                    "stock_kg": float(pid.stock_kg),
                })
            elif isinstance(pid, DigitalProduct):
                items.append({
                    "id": pid.id,
                    "type": "digital",
                    "name": pid.name,
                    "category": pid.category,
                    "price": str(pid.price),
                })

        with open(self.catalog_path, "w", encoding="utf-8") as f:
            json.dump({"products": items}, f, ensure_ascii=False, indent=2)
