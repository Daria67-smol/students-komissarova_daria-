from abc import ABC, abstractmethod
from decimal import Decimal, ROUND_HALF_UP
from shop.exceptions import InvalidQuantityError, OutOfStockError

class Product(ABC):
    def __init__(self, product_id: str, name: str, category: str, price: float):
        self._id = product_id
        self._name = name
        self._category = category
        self._price = Decimal(str(price))

    @property
    def id(self) -> str:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @property
    def category(self) -> str:
        return self._category

    @property
    def price(self) -> Decimal:
        return self._price

    @abstractmethod
    def line_price(self, qty: float) -> Decimal:
        "Стоимость строки корзины для данного количества."
        pass

    @abstractmethod
    def check_qty(self, qty: float) -> None:
        "Проверка допустимости количества. Кидает исключение при ошибке."
        pass

    @abstractmethod
    def consume_stock(self, qty: float) -> None:
        "Списать со склада. Кидает исключение при нехватке."
        pass


class PieceProduct(Product):
    def __init__(self, product_id: str, name: str, category: str, price: float, stock: int):
        super().__init__(product_id, name, category, price)
        self._stock = int(stock)

    @property
    def stock(self) -> int:
        return self._stock

    def line_price(self, qty: float) -> Decimal:
        if not float(qty).is_integer():
            raise InvalidQuantityError("Штучный товар можно добавлять только целым количеством.")
        return self.price * int(qty)

    def check_qty(self, qty: float) -> None:
        if not float(qty).is_integer():
            raise InvalidQuantityError("Количество штучного товара должно быть целым.")
        if int(qty) <= 0:
            raise InvalidQuantityError("Количество должно быть больше 0.")
        if int(qty) > self._stock:
            raise OutOfStockError(f"Недостаточно товара {self._name} на складе.")

    def consume_stock(self, qty: float) -> None:
        qty_int = int(qty)
        self.check_qty(qty_int)
        self._stock -= qty_int


class WeightProduct(Product):
    def __init__(self, product_id: str, name: str, category: str, price_per_kg: float, min_kg: float, stock_kg: float):
        super().__init__(product_id, name, category, price_per_kg)
        self._min_kg = Decimal(str(min_kg))
        self._stock_kg = Decimal(str(stock_kg))

    @property
    def min_kg(self) -> Decimal:
        return self._min_kg

    @property
    def stock_kg(self) -> Decimal:
        return self._stock_kg

    def line_price(self, qty: float) -> Decimal:
        qty_dec = Decimal(str(qty))
        total = self.price * qty_dec
        return total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def check_qty(self, qty: float) -> None:
        qty_dec = Decimal(str(qty))
        if qty_dec <= 0:
            raise InvalidQuantityError("Количество весового товара должно быть больше 0.")
        if qty_dec < self._min_kg:
            raise InvalidQuantityError(f"Минимальное количество для {self._name} — {self._min_kg} кг.")
        if qty_dec > self._stock_kg:
            raise OutOfStockError(f"Недостаточно товара {self._name} на складе.")

    def consume_stock(self, qty: float) -> None:
        qty_dec = Decimal(str(qty))
        self.check_qty(qty_dec)
        self._stock_kg -= qty_dec


class DigitalProduct(Product):
    def __init__(self, product_id: str, name: str, category: str, price: float):
        super().__init__(product_id, name, category, price)

    def line_price(self, qty: float) -> Decimal:
        if qty != 1:
            raise InvalidQuantityError("Цифровой товар можно добавить только в количестве 1.")
        return self.price

    def check_qty(self, qty: float) -> None:
        if qty != 1:
            raise InvalidQuantityError("Цифровой товар можно добавить только в количестве 1.")

    def consume_stock(self, qty: float) -> None:
        # Цифровые товары не имеют склада
        self.check_qty(qty)
