from random import randint


def generate_account_number():
    return '20' + str(randint(10000000, 99999999))
