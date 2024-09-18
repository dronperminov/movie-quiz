import hashlib
import os
from typing import List


def __get_hash(filename: str) -> str:
    hash_md5 = hashlib.md5()

    with open(filename, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)

    return hash_md5.hexdigest()


def get_static_hash() -> str:
    hashes = []

    for directory in ["js", "styles"]:
        for path, _, files in os.walk(os.path.join(os.path.dirname(__file__), "..", "..", "web", directory)):
            for name in files:
                hashes.append(__get_hash(os.path.join(path, name)))

    static_hash = "_".join(hashes)
    hash_md5 = hashlib.md5()
    hash_md5.update(static_hash.encode("utf-8"))
    return hash_md5.hexdigest()


def get_word_form(count: int, word_forms: List[str], only_form: bool = False) -> str:
    index = 0

    if abs(count) % 10 in {0, 5, 6, 7, 8, 9} or abs(count) % 100 in {10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20}:
        index = 2
    elif abs(count) % 10 in {2, 3, 4}:
        index = 1

    return word_forms[index] if only_form else f"{count} {word_forms[index]}"


def format_time(total: float) -> str:
    if total < 60:
        return f"{round(total, 1)} сек."

    seconds = round(total)
    minutes = (seconds // 60) % 60
    hours = seconds // 3600
    seconds = seconds % 60

    if total < 3600:
        return f"{minutes:02} мин. {seconds:02} сек."

    return f"{hours} ч. {minutes:02} мин."
