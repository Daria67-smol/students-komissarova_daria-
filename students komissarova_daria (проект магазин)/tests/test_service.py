import pytest
from decimal import Decimal, ROUND_HALF_UP
from shop.exceptions import OutOfStockError, OrderError, ProductNotFoundError


def test_checkout_reduces_stock(shop_service):
    product = shop_service.products["P001"]
    initial_stock = product.stock  # лучше через публичный геттер/свойство

    shop_service.add_to_cart("P001", 2)
    order = shop_service.checkout()

    assert order is not None
    assert product.stock == initial_stock - 2


def test_add_to_cart_fails_when_out_of_stock(shop_service):
    """Проверка, что нельзя добавить больше, чем есть на складе (на уровне корзины)."""
    product = shop_service.products["P001"]

    with pytest.raises(OutOfStockError):
        # Пытаемся добавить больше, чем есть
        shop_service.add_to_cart("P001", product.stock + 1)


def test_checkout_fails_when_stock_insufficient(shop_service):
    """
    Если проверка остатков только при чекауте (а не при добавлении),
    то ошибка должна быть здесь.
    """
    product = shop_service.products["P001"]

    # Добавляем ровно столько, сколько есть
    shop_service.add_to_cart("P001", product.stock)
    # Теперь пробуем добавить ещё
    shop_service.add_to_cart("P001", 1)  # если проверка только при чекауте — это ок

    with pytest.raises(OutOfStockError):
        shop_service.checkout()


def test_cancel_order_restores_stock(shop_service):
    product = shop_service.products["P001"]
    initial_stock = product.stock

    qty = 2
    shop_service.add_to_cart("P001", qty)
    order = shop_service.checkout()
    assert product.stock == initial_stock - qty

    shop_service.cancel_order(order.id)

    # После отмены склад должен вернуться к исходному значению
    assert product.stock == initial_stock


def test_cancel_already_cancelled_order_raises(shop_service):
    qty = 1
    shop_service.add_to_cart("P001", qty)
    order = shop_service.checkout()

    # Первая отмена — ок
    shop_service.cancel_order(order.id)

    # Повторная отмена должна вызвать ошибку
    with pytest.raises(OrderError):
        shop_service.cancel_order(order.id)
