import math


class CalculatorError(Exception):
    """Custom error type for predictable calculator failures."""


def add(a, b):
    return a + b


def subtract(a, b):
    return a - b


def multiply(a, b):
    return a * b


def divide(a, b):
    if b == 0:
        raise CalculatorError("Division by zero is not allowed.")
    return a / b


def floor_divide(a, b):
    if b == 0:
        raise CalculatorError("Floor division by zero is not allowed.")
    return a // b


def modulo(a, b):
    if b == 0:
        raise CalculatorError("Modulo by zero is not allowed.")
    return a % b


def power(a, b):
    return math.pow(a, b)


def square_root(a):
    if a < 0:
        raise CalculatorError("Cannot calculate square root of a negative number.")
    return math.sqrt(a)


def absolute(a):
    return abs(a)


def factorial(a):
    if not float(a).is_integer() or a < 0:
        raise CalculatorError("Factorial requires a non-negative whole number.")
    return math.factorial(int(a))


def percent_of(a, b):
    return (a / 100) * b


OPERATIONS = {
    "+": {"fn": add, "arity": 2, "description": "Addition"},
    "-": {"fn": subtract, "arity": 2, "description": "Subtraction"},
    "*": {"fn": multiply, "arity": 2, "description": "Multiplication"},
    "/": {"fn": divide, "arity": 2, "description": "Division"},
    "//": {"fn": floor_divide, "arity": 2, "description": "Floor division"},
    "%": {"fn": modulo, "arity": 2, "description": "Modulo"},
    "pow": {"fn": power, "arity": 2, "description": "Power"},
    "sqrt": {"fn": square_root, "arity": 1, "description": "Square root"},
    "abs": {"fn": absolute, "arity": 1, "description": "Absolute value"},
    "fact": {"fn": factorial, "arity": 1, "description": "Factorial"},
    "pct": {"fn": percent_of, "arity": 2, "description": "Percent of"},
}
