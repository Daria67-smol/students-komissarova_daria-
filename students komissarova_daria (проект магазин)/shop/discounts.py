from decimal import Decimal
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from shop.cart import Cart  # для статического анализа
from abc import ABC, abstractmethod


class Discount(ABC):
    """Базовый класс для всех скидок."""

    @abstractmethod
    def apply(self, cart: Cart) -> Decimal:
        """Возвращает сумму скидки для корзины."""
        pass


class PercentDiscount:
    def __init__(self, code: str, percent: int):
        self.code = code
        self.percent = percent

    def apply(self, cart: "Cart") -> Decimal:
        subtotal = cart.subtotal
        return subtotal * Decimal(str(self.percent)) / Decimal("100")


class FixedDiscount:
    def __init__(self, code: str, amount: Decimal, min_total: Decimal | None = None):
        self.code = code
        self.amount = amount
        self.min_total = min_total

    def apply(self, cart: "Cart") -> Decimal:
        subtotal = cart.subtotal

        if self.min_total is not None and subtotal < self.min_total:
            return Decimal("0")

        return min(self.amount, subtotal)


def create_discount(code: str, config: dict):
    discount_type = config.get("type")

    if discount_type == "percent":
        percent = config.get("percent", 0)
        return PercentDiscount(code, int(percent))

    elif discount_type == "fixed":
        amount_raw = config.get("amount")
        min_total_raw = config.get("min_total")

        amount = (
            Decimal(str(amount_raw))
            if not isinstance(amount_raw, Decimal)
            else amount_raw
        )
        min_total = None
        if min_total_raw is not None:
            min_total = (
                Decimal(str(min_total_raw))
                if not isinstance(min_total_raw, Decimal)
                else min_total_raw
            )

        return FixedDiscount(code, amount, min_total)

    else:
        raise ValueError(f"Неизвестный тип скидки: {discount_type}")
