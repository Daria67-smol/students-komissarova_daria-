import pytest
from shop.products import PieceProduct, WeightProduct, DigitalProduct

def test_piece_product_line_price():
    p = PieceProduct("P001", "Кружка", "merch", 590, 10)
    assert p.line_price(2) == 1180

def test_weight_product_line_price_rounds():
    p = WeightProduct("P010", "Чай", "tea", 2400, 0.1, 5.0)
    # 0.35 кг * 2400 = 840.00
    assert p.line_price(0.35) == 840.00

def test_digital_product_line_price():
    p = DigitalProduct("P020", "Курс", "courses", 1990)
    assert p.line_price(1) == 1990

def test_piece_product_invalid_qty():
    p = PieceProduct("P001", "Кружка", "merch", 590, 10)
    with pytest.raises(Exception):
        p.check_qty(1.5)

def test_weight_product_min_qty():
    p = WeightProduct("P010", "Чай", "tea", 2400, 0.1, 5.0)
    with pytest.raises(Exception):
        p.check_qty(0.05)

def test_digital_product_only_one():
    p = DigitalProduct("P020", "Курс", "courses", 1990)
    with pytest.raises(Exception):
        p.check_qty(2)
