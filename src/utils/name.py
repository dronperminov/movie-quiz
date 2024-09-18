import re


def get_first_letter(name: str) -> str:
    return re.findall(r"[a-zа-яё\d]", name.lower())[0]


def get_last_letter(name: str) -> str:
    return re.findall(r"[a-zа-яё\d]", name.lower())[-1]


def get_name_length(name: str) -> int:
    return len(re.findall(r"[a-zа-яё\d]", name.lower()))
