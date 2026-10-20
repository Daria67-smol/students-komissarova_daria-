from decimal import Decimal
from shop.products import PieceProduct
from shop.discounts import PercentDiscount, FixedDiscount
from shop.cart import Cart


def test_percent_discount():
    d = PercentDiscount("SALE10", Decimal("10"))
    cart = Cart()

    # Добавляем товар, чтобы subtotal реально посчитался
    product = PieceProduct("P1", "Кружка", "merch", Decimal("1000"), 10)
    cart._product_map = {"P1": product}
    cart.add_item("P1", 1)  # subtotal станет 1000

    discount_amount = d.apply(cart)

    assert discount_amount == Decimal("100.00")  # 10% от 1000


def test_fixed_discount_below_threshold():
    d = FixedDiscount("FIXED500", Decimal("500"), Decimal("3000"))  # скидка 500 ₽, порог 3000 ₽
    cart = Cart()

    product = PieceProduct("P2", "Тарелка", "merch", Decimal("2000"), 5)
    cart._product_map = {"P2": product}
    cart.add_item("P2", 1)  # subtotal = 2000 (< порога)

    discount_amount = d.apply(cart)

    assert discount_amount == Decimal("0.00")


def test_fixed_discount_above_threshold():
    d = FixedDiscount("FIX500", Decimal("500"), Decimal("3000"))  # скидка 500 ₽, порог 3000 ₽
    cart = Cart()

    product = PieceProduct("P3", "Набор тарелок", "merch", Decimal("4000"), 3)
    cart._product_map = {"P3": product}
    cart.add_item("P3", 1)  # subtotal = 4000 (> порога)

    discount_amount = d.apply(cart)

    assert discount_amount == Decimal("500.00")
