import pytest

from operations import (
    CalculatorError,
    absolute,
    add,
    divide,
    factorial,
    floor_divide,
    modulo,
    multiply,
    percent_of,
    power,
    square_root,
    subtract,
)


def test_basic_operations():
    assert add(2, 3) == 5
    assert subtract(10, 4) == 6
    assert multiply(3, 7) == 21


def test_extended_operations():
    assert divide(10, 2) == 5
    assert floor_divide(7, 2) == 3
    assert modulo(7, 4) == 3
    assert power(2, 3) == 8
    assert square_root(81) == 9
    assert absolute(-19.5) == 19.5
    assert factorial(5) == 120
    assert percent_of(20, 150) == 30


def test_division_errors():
    with pytest.raises(CalculatorError):
        divide(1, 0)
    with pytest.raises(CalculatorError):
        floor_divide(1, 0)
    with pytest.raises(CalculatorError):
        modulo(1, 0)


def test_unary_validation_errors():
    with pytest.raises(CalculatorError):
        square_root(-1)
    with pytest.raises(CalculatorError):
        factorial(-4)
    with pytest.raises(CalculatorError):
        factorial(3.2)
