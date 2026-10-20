from dataclasses import dataclass
from decimal import Decimal
from typing import List, Literal

OrderStatus = Literal["new", "cancelled", "completed"]

@dataclass
class OrderItemSnapshot:
    product_id: str
    qty: float
    price: Decimal
    line_total: Decimal

@dataclass
class Order:
    id: int
    items: List[OrderItemSnapshot]
    subtotal: Decimal
    discount: Decimal
    total: Decimal
    promo: str
    status: OrderStatus
    created_at: str

    def __str__(self) -> str:
        lines = [
            f"Заказ #{self.id} [{self.status}]",
            f"Дата: {self.created_at}",
            f"Позиций: {len(self.items)}, Сумма: {self.subtotal} ₽",
            f"Скидка: {self.discount} ₽, Итого: {self.total} ₽",
            f"Промокод: {self.promo or 'нет'}",
        ]
        for item in self.items:
            lines.append(f"  - {item.product_id}: {item.qty} шт. × {item.price} = {item.line_total} ₽")
        return "\n".join(lines)
