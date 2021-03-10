from os import urandom


def random_hex(length=20):
    """"""
    return urandom(length).hex()


def obfuscate(value):
    clear_length = len(value) // 2
    return value[:clear_length] + ("*" * (len(value) - clear_length))
