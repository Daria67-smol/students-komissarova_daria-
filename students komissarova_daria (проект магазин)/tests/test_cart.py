import pytest
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

from shop.products import PieceProduct
from shop.repository import Repository
from shop.service import ShopService


@pytest.fixture
def shop_service(tmp_path):
    data_path = tmp_path / "data"
    data_path.mkdir(parents=True, exist_ok=True)

    repo = Repository(data_path)

    # Создаём тестовый каталог
    catalog = {
        "P001": PieceProduct("P001", "Кружка", "merch", Decimal("500"), 10),
        "P002": PieceProduct("P002", "Тарелка", "merch", Decimal("300"), 5),
    }
    repo.save_catalog(catalog)

    service = ShopService(repo, Path("log.txt"))
    return service


def test_cart_add_item(shop_service):
    assert "P001" in shop_service.products, "Товар P001 должен быть в каталоге для теста"
    product = shop_service.products["P001"]
    price = product.price

    shop_service.add_to_cart("P001", 2)

    assert len(shop_service.cart) == 1
    expected_subtotal = price * Decimal("2")
    assert shop_service.cart.subtotal == expected_subtotal.quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )


def test_cart_set_item_updates_qty(shop_service):
    assert "P001" in shop_service.products
    product = shop_service.products["P001"]
    price = product.price

    shop_service.add_to_cart("P001", 2)
    shop_service.set_cart_item("P001", 5)  # обновляем количество

    # После set_item количество должно измениться с 7 до 5
    assert len(shop_service.cart) == 1
    expected_subtotal = price * Decimal("5")
    assert shop_service.cart.subtotal == expected_subtotal.quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )


def test_cart_remove_item(shop_service):
    assert "P001" in shop_service.products

    shop_service.add_to_cart("P001", 2)
    assert len(shop_service.cart) == 1

    shop_service.remove_from_cart("P001")

    assert not shop_service.cart  # корзина пуста (bool == False)
    assert len(shop_service.cart) == 0


def test_cart_bool_empty_when_no_items():
    from shop.cart import Cart

    cart = Cart()
    assert not cart
    assert len(cart) == 0
