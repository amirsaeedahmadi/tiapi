from secrets import choice
from string import digits


def generate_integer_code(length=5):
    return choice(digits[1:]) + "".join(choice(digits) for i in range(length - 1))
