def tambah(a: float, b: float) -> float:
    """Tambah dua bilangan."""
    return a + b


def kurang(a: float, b: float) -> float:
    """Kurang bilangan b dari a."""
    return a - b


def kali(a: float, b: float) -> float:
    """Kali dua bilangan."""
    return a * b


def bagi(a: float, b: float) -> float:
    """Bagi bilangan a dengan b."""
    if b == 0:
        raise ValueError("Pembagi nol")
    return a / b


if __name__ == "__main__":
    assert tambah(10, 5) == 15
    assert kurang(10, 5) == 5
    assert kali(10, 5) == 50
    assert bagi(10, 5) == 2.0
    try:
        bagi(10, 0)
    except ValueError:
        pass
    print("Tes lolos.")
