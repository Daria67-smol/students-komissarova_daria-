from decimal import Decimal
from pathlib import Path
from typing import Dict, List
from datetime import datetime
from shop.discounts import Discount
from shop.products import Product, PieceProduct, WeightProduct
from shop.cart import Cart
from shop.orders import Order, OrderItemSnapshot
from shop.repository import Repository
from shop.exceptions import (
    ProductNotFoundError, InvalidQuantityError,
    InvalidPromoError, EmptyCartError, OrderError
)
from shop.decorators import log_action
from dataclasses import asdict


class ShopService:
    def __init__(self, repo: Repository, log_path: Path):
        self.repo = repo
        self.log_path = log_path
        self.products: Dict[str, Product] = {}
        self.promos: Dict[str, Discount] = {}  # тип для IDE, без реального импорта
        self.cart = Cart()
        self.orders: List[Order] = []
        self.next_order_id: int = 1

        self._load_data()

    # Методы корзины (с декоратором)
    @log_action(Path("data/shop.log"))
    def add_to_cart(self, product_id: str, qty: float) -> None:
        if product_id not in self.products:
            raise ProductNotFoundError(f"Товар {product_id} не найден")

        product = self.products[product_id]
        product.check_qty(qty)

        self.cart.add_item(product_id, qty)
        self._save_state()

    @log_action(Path("data/shop.log"))
    def set_cart_item(self, product_id: str, qty: float) -> None:
        if product_id not in self.products:
            raise ProductNotFoundError(f"Товар {product_id} не найден.")
        self.cart.set_item(product_id, qty)
        self._save_state()

    @log_action(Path("data/shop.log"))
    def remove_from_cart(self, product_id: str) -> None:
        self.cart.remove_item(product_id)
        self._save_state()

    @log_action(Path("data/shop.log"))
    def apply_promo(self, code: str) -> None:
        if code not in self.promos:
            raise InvalidPromoError(f"Промокод {code} не найден.")
        self.cart.set_promo(code, discounts=self.promos)
        self._save_state()

    # Оформление заказа
    @log_action(Path("data/shop.log"))
    def checkout(self) -> Order:
        if not self.cart:
            raise EmptyCartError("Корзина пуста, нельзя оформить заказ.")

        # 1. Проверяем остатки
        for item in self.cart.items:
            product = self.products[item.product_id]
            product.check_qty(item.qty)

        # 2. Считаем стоимость
        order_items = []
        subtotal = Decimal("0")
        for item in self.cart.items:
            product = self.products[item.product_id]
            line_total = product.line_price(item.qty)
            order_items.append(OrderItemSnapshot(item.product_id, item.qty, product.price, line_total))
            subtotal += line_total

        # 3. Применяем скидку
        promo_code = self.cart.promo
        discount = Decimal("0")

        if promo_code and promo_code in self.promos:
            discount = self.promos[promo_code].apply(self.cart)

        total = max(subtotal - discount, Decimal("0"))

        # 4. Создаём заказ
        order = Order(
            id=self.next_order_id,
            items=order_items,
            subtotal=subtotal,
            discount=discount,
            total=total,
            promo=promo_code,
            status="new",
            created_at=datetime.now().isoformat()
        )
        self.orders.append(order)
        self.next_order_id += 1

        # 5. Списываем остатки
        for item in order.items:
            product = self.products[item.product_id]
            product.consume_stock(item.qty)

        # 6. Очищаем корзину
        self.cart = Cart()
        self.cart._product_map = self.products
        self._save_state()
        return order

    # Отмена заказа
    @log_action(Path("data/shop.log"))
    def cancel_order(self, order_id: int) -> None:
        order = next((o for o in self.orders if o.id == order_id), None)
        if not order:
            raise OrderError(f"Заказ #{order_id} не найден.")

        if order.status == "cancelled":
            raise OrderError(f"Заказ #{order_id} уже отменён.")

        # Возвращаем остатки
        for item in order.items:
            if item.product_id in self.products:
                product = self.products[item.product_id]
                product.restock(item.qty)

        order.status = "cancelled"
        self._save_state()

    # Прочее
    @log_action(Path("data/shop.log"))
    def restock(self, product_id: str, qty: float) -> None:
        if product_id not in self.products:
            raise ProductNotFoundError(f"Товар {product_id} не найден.")
        product = self.products[product_id]

        if isinstance(product, (PieceProduct, WeightProduct)):
            product.restock(Decimal(str(qty)))
        else:
            raise InvalidQuantityError("Нельзя пополнить склад для цифрового товара.")

        self._save_state()

    # Загрузка и сохранение состояния
    def _load_data(self) -> None:
        self.products = self.repo.load_catalog()
        self.promos = self.repo.load_promos()
        orders_data = self.repo.load_orders()

        self.cart._product_map = self.products

        cart_data = orders_data.get("cart", {})
        for item in cart_data.get("items", []):
            pid = item["product_id"]
            qty = item["qty"]
            if pid not in self.products:
                continue
            self.cart.add_item(pid, float(qty))

        promo_code = cart_data.get("promo")
        if promo_code:
            self.cart.set_promo(promo_code, discounts=self.promos)

        self.orders = []
        for o in orders_data.get("orders", []):
            items = [
                OrderItemSnapshot(
                    i["product_id"],
                    Decimal(str(i["qty"])),
                    Decimal(str(i["price"])),
                    Decimal(str(i["line_total"]))
                )
                for i in o.get("items", [])
            ]
            order = Order(
                id=o["id"],
                items=items,
                subtotal=Decimal(str(o["subtotal"])),
                discount=Decimal(str(o["discount"])),
                total=Decimal(str(o["total"])),
                promo=o.get("promo"),
                status=o["status"],
                created_at=o.get("created_at", "")
            )
            self.orders.append(order)

        self.next_order_id = orders_data.get("next_order_id", 1)

    def _save_state(self) -> None:
        self.repo.save_catalog(self.products)

        cart_items = [
            {"product_id": i.product_id, "qty": str(i.qty)}
            for i in self.cart.items
        ]

        orders_data = {
            "cart": {"items": cart_items, "promo": self.cart.promo},
            "orders": [asdict(o) for o in self.orders],
            "next_order_id": self.next_order_id
        }
        self.repo.save_orders(orders_data)
