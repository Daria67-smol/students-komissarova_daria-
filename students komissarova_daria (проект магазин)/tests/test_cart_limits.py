import pytest
from decimal import Decimal
from shop.products import WeightProduct, DigitalProduct, PieceProduct
from shop.cart import Cart
from shop.exceptions import InvalidQuantityError


@pytest.fixture
def weight_product():
    return WeightProduct("W1", "Чай на развес", "tea", Decimal("2000"), 0.1, 1.0)


@pytest.fixture
def digital_product():
    return DigitalProduct("D1", "Ключ доступа", "digital", Decimal("900"))


@pytest.fixture
def piece_product():
    return PieceProduct("P1", "Кружка", "merch", Decimal("600"), 5)


def test_weight_product_min_qty_enforced(weight_product):
    cart = Cart()
    cart._product_map = {"W1": weight_product}

    with pytest.raises(InvalidQuantityError):
        cart.add_item("W1", 0.05)


def test_weight_product_allowed_qty(weight_product):
    cart = Cart()
    cart._product_map = {"W1": weight_product}

    cart.add_item("W1", 0.2)
    assert len(cart.items) == 1


def test_digital_product_max_qty_one(digital_product):
    cart = Cart()
    cart._product_map = {"D1": digital_product}

    with pytest.raises(InvalidQuantityError):
        cart.add_item("D1", 2)


def test_piece_product_fractional_qty_rejected(piece_product):
    cart = Cart()
    cart._product_map = {"P1": piece_product}

    with pytest.raises(InvalidQuantityError):
        cart.add_item("P1", 1.5)


def test_piece_product_integer_qty_allowed(piece_product):
    cart = Cart()
    cart._product_map = {"P1": piece_product}

    cart.add_item("P1", 3)
    assert len(cart.items) == 1
