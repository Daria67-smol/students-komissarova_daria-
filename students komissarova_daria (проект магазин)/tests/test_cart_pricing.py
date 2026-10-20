import pytest
from decimal import Decimal, ROUND_HALF_UP
from shop.products import WeightProduct, PieceProduct
from shop.cart import Cart


@pytest.fixture
def weight_product_2400():
    return WeightProduct("W2", "Чай", "tea", Decimal("2400"), 0.1, 5.0)


@pytest.fixture
def piece_product_590():
    return PieceProduct("P2", "Кружка", "merch", Decimal("590"), 10)


def test_weight_product_line_price_correct(weight_product_2400):
    cart = Cart()
    cart._product_map = {"W2": weight_product_2400}

    cart.add_item("W2", 0.35)  # передача ID и количества

    # Получаем товар и считаем line_total вручную, как это делает корзина
    product = cart._product_map["W2"]
    qty = Decimal("0.35")
    line_total = product.line_price(float(qty)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    assert line_total == Decimal("840.00")  # 2400 * 0.35 = 840


def test_weight_product_rounding_edge_case(weight_product_2400):
    cart = Cart()
    cart._product_map = {"W2": weight_product_2400}

    qty_val = Decimal("0.333")
    cart.add_item("W2", float(qty_val))

    product = cart._product_map["W2"]
    expected = (product.price * qty_val).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    actual = product.line_price(float(qty_val)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    assert actual == expected


def test_piece_product_line_total_correct(piece_product_590):
    cart = Cart()
    cart._product_map = {"P2": piece_product_590}

    cart.add_item("P2", 3)

    product = cart._product_map["P2"]
    line_total = product.line_price(3).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    assert line_total == Decimal("1770.00")  # 590 * 3
