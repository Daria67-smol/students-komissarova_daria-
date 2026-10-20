class ShopError(Exception):
    "Базовый класс для всех ошибок магазина."
    pass

class ProductNotFoundError(ShopError):
    pass

class OutOfStockError(ShopError):
    pass

class InvalidQuantityError(ShopError):
    pass

class InvalidPromoError(ShopError):
    pass

class EmptyCartError(ShopError):
    pass

class OrderError(ShopError):
    pass

