import string

BASE62 = string.digits + string.ascii_letters
BASE = len(BASE62)


def base62_encode(num: int) -> str:
    if num == 0:
        return BASE62[0]

    result = []
    while num:
        num, rem = divmod(num, BASE)
        result.append(BASE62[rem])

    return "".join(reversed(result))


def base62_decode(s: str) -> int:
    num = 0
    for char in s:
        num = num * BASE + BASE62.index(char)

    return num
