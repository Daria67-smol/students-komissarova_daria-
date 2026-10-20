from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from typing import List, Optional, Dict
from shop.discounts import Discount
from shop.products import Product
from shop.exceptions import ProductNotFoundError

@dataclass
class CartItem:
    product_id: str
    qty: Decimal


class Cart:
    def __init__(self) -> None:
        self._items: List[CartItem] = []
        self._product_map: Optional[Dict[str, Product]] = None
        self._promo_code: Optional[str] = None
        self._discount: Optional[Discount] = None

    @property
    def promo(self) -> Optional[str]:
        """Для совместимости с ShopService._save_state."""
        return self._promo_code

    @promo.setter
    def promo(self, value: Optional[str]) -> None:
        self._promo_code = value

    def set_promo(
        self,
        code: Optional[str],
        discounts: Optional[Dict[str, Discount]] = None,
    ) -> None:
        """
        Устанавливает промокод.
        Если передан словарь скидок (promo_code -> Discount), сразу пытается найти скидку.
        Иначе код просто сохраняется, а скидка будет подгружена позже (например, в ShopService).
        """
        self._promo_code = code
        if code is None:
            self._discount = None
            return

        if discounts and code in discounts:
            self._discount = discounts[code]
        else:
            self._discount = None

    @property
    def subtotal(self) -> Decimal:
        if self._product_map is None:
            return Decimal("0")

        total = Decimal("0")
        for item in self._items:
            product = self._product_map.get(item.product_id)
            if not product:
                continue
            line_total = product.price * item.qty
            total += line_total

        return total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    @property
    def total(self) -> Decimal:
        subtotal = self.subtotal
        discount_amount = Decimal("0")

        if self._discount is not None:
            discount_amount = self._discount.apply(self)

        final = subtotal - discount_amount
        if final < 0:
            final = Decimal("0")

        return final.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def add_item(self, product_id: str, qty: float) -> None:
        if self._product_map is None:
            raise RuntimeError(
                "Не задан product_map для корзины (self.cart._product_map = products)"
            )

        if product_id not in self._product_map:
            raise ProductNotFoundError(f"Товар {product_id} не найден.")

        product = self._product_map[product_id]
        qty_dec = Decimal(str(qty))
        product.check_qty(float(qty_dec))

        for item in self._items:
            if item.product_id == product_id:
                new_qty = item.qty + qty_dec
                product.check_qty(float(new_qty))
                item.qty = new_qty
                return

        self._items.append(CartItem(product_id=product_id, qty=qty_dec))

    def set_item(self, product_id: str, qty: float) -> None:
        if qty <= 0:
            self.remove_item(product_id)
            return

        if self._product_map is None:
            raise RuntimeError("Не задан product_map для корзины")

        if product_id not in self._product_map:
            raise ProductNotFoundError(f"Товар {product_id} не найден.")

        product = self._product_map[product_id]
        product.check_qty(qty)

        for item in self._items:
            if item.product_id == product_id:
                item.qty = Decimal(str(qty))
                return

        self._items.append(CartItem(product_id=product_id, qty=Decimal(str(qty))))

    def remove_item(self, product_id: str) -> None:
        self._items = [item for item in self._items if item.product_id != product_id]

    @property
    def items(self) -> List[CartItem]:
        return self._items

    def clear(self) -> None:
        self._items.clear()

    #  Магические методы
    def __len__(self) -> int:
        return len(self._items)

    def __bool__(self) -> bool:
        return bool(self._items)

    def __contains__(self, product_id: str) -> bool:
        return any(item.product_id == product_id for item in self._items)

    def __iter__(self):
        return iter(self._items)
