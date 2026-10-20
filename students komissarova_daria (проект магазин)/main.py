import sys
import argparse
from pathlib import Path
from shop.service import ShopService
from shop.exceptions import ShopError
from shop.products import PieceProduct, WeightProduct, DigitalProduct
from shop.repository import Repository

def main():
    parser = argparse.ArgumentParser(description="Консольный интернет‑магазин")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # catalog
    p_catalog = subparsers.add_parser("catalog", help="Показать каталог")
    p_catalog.add_argument("--category", help="Фильтр по категории")

    # search
    p_search = subparsers.add_parser("search", help="Поиск по названию")
    p_search.add_argument("query", help="Поисковый запрос")

    # show
    p_show = subparsers.add_parser("show", help="Показать товар по ID")
    p_show.add_argument("product_id", help="Артикул товара")

    # cart
    p_cart = subparsers.add_parser("cart", help="Управление корзиной")
    cart_sub = p_cart.add_subparsers(dest="action", required=True)
    cart_add = cart_sub.add_parser("add", help="Добавить в корзину")
    cart_add.add_argument("product_id", help="Артикул")
    cart_add.add_argument("qty", type=float, help="Количество")
    cart_set = cart_sub.add_parser("set", help="Установить количество")
    cart_set.add_argument("product_id", help="Артикул")
    cart_set.add_argument("qty", type=float, help="Количество")
    cart_remove = cart_sub.add_parser("remove", help="Убрать из корзины")
    cart_remove.add_argument("product_id", help="Артикул")
    cart_show = cart_sub.add_parser("show", help="Показать корзину")

    # promo
    p_promo = subparsers.add_parser("promo", help="Применить промокод")
    p_promo.add_argument("code", help="Код промокода")

    # checkout
    p_checkout = subparsers.add_parser("checkout", help="Оформить заказ")

    # orders
    p_orders = subparsers.add_parser("orders", help="Список заказов")

    # order
    p_order = subparsers.add_parser("order", help="Показать заказ по ID")
    p_order.add_argument("order_id", type=int, help="Номер заказа")

    # cancel
    p_cancel = subparsers.add_parser("cancel", help="Отменить заказ")
    p_cancel.add_argument("order_id", type=int, help="Номер заказа")

    # restock
    p_restock = subparsers.add_parser("restock", help="Пополнить склад")
    p_restock.add_argument("product_id", help="Артикул")
    p_restock.add_argument("qty", type=float, help="Количество")

    # export-orders
    p_export = subparsers.add_parser("export-orders", help="Экспорт заказов в CSV")
    p_export.add_argument("path", help="Путь к CSV‑файлу")

    args = parser.parse_args()

    data_path = Path("data")
    data_path.mkdir(exist_ok=True)
    service = ShopService(repo=Repository(data_path), log_path=data_path / "shop.log")

    try:
        if args.command == "catalog":
            if args.category:
                products = [p for p in service.products.values() if p.category == args.category]
            else:
                products = list(service.products.values())
            for p in products:
                print(f"{p.id} | {p.name} | {p.category} | {p.price} ₽ | Остаток: {getattr(p, 'stock', getattr(p, 'stock_kg', '—'))}")

        elif args.command == "search":
            query = args.query.lower()
            products = [p for p in service.products.values() if query in p.name.lower()]
            for p in products:
                print(f"{p.id} | {p.name} | {p.category} | {p.price} ₽")

        elif args.command == "show":
            pid = args.product_id
            if pid not in service.products:
                print(f"Товар {pid} не найден.")
                return
            p = service.products[pid]
            print(f"Артикул: {p.id}")
            print(f"Название: {p.name}")
            print(f"Категория: {p.category}")
            print(f"Цена: {p.price} ₽")
            if isinstance(p, PieceProduct):
                print(f"Тип: штучный, остаток: {p.stock}")
            elif isinstance(p, WeightProduct):
                print(f"Тип: весовой, цена за кг: {p.price}, мин. вес: {p.min_kg}, остаток: {p.stock_kg} кг")
            elif isinstance(p, DigitalProduct):
                print("Тип: цифровой, склада нет")

        elif args.command == "cart":
            if args.action == "add":
                service.add_to_cart(args.product_id, args.qty)
                print("Товар добавлен в корзину.")
            elif args.action == "set":
                service.set_cart_item(args.product_id, args.qty)
                print("Количество обновлено.")
            elif args.action == "remove":
                service.remove_from_cart(args.product_id)
                print("Товар удалён из корзины.")
            elif args.action == "show":
                if not service.cart:
                    print("Корзина пуста.")
                    return
                for item in service.cart.items:
                    print(f"{item.product_id} | {item.qty} | {item.line_total} ₽")
                print(f"Промежуточная сумма: {service.cart.subtotal} ₽")
                print(f"Промокод: {service.cart.promo or 'нет'}")

        elif args.command == "promo":
            service.apply_promo(args.code)
            print(f"Промокод {args.code} применён.")

        elif args.command == "checkout":
            order = service.checkout()
            print("Заказ оформлен:")
            print(order)

        elif args.command == "orders":
            for o in service.orders:
                print(f"#{o.id} | {o.status} | {len(o.items)} позиций | {o.total} ₽")

        elif args.command == "order":
            order = next((o for o in service.orders if o.id == args.order_id), None)
            if not order:
                print(f"Заказ #{args.order_id} не найден.")
                return
            print(order)

        elif args.command == "cancel":
            service.cancel_order(args.order_id)
            print(f"Заказ #{args.order_id} отменён.")

        elif args.command == "restock":
            service.restock(args.product_id, args.qty)
            print(f"Склад пополнен: {args.qty} шт./кг для {args.product_id}")

        elif args.command == "export-orders":
            import csv
            path = Path(args.path)
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["id", "status", "items_count", "subtotal", "discount", "total", "promo"])
                for o in service.orders:
                    writer.writerow([
                        o.id, o.status, len(o.items), o.subtotal, o.discount, o.total, o.promo
                    ])
            print(f"Заказы экспортированы в {path}")

    except ShopError as e:
        print(f"Ошибка: {e}")
    except Exception as e:
        print(f"Неожиданная ошибка: {e}")

if __name__ == "__main__":
    main()