from os import urandom


def random_hex(length=20):
    """
    """
    return urandom(length).hex()
