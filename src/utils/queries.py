from enum import Enum
from typing import Dict, Iterable, Union


def interval_query(name: str, interval: Iterable[Union[str, float, int]]) -> dict:
    value_from, value_to = interval
    query = {}

    if isinstance(value_from, float) or isinstance(value_from, int):
        query["$gte"] = value_from

    if isinstance(value_to, float) or isinstance(value_to, int):
        query["$lte"] = value_to

    return {name: query} if query else {}


def enum_query(name: str, values: Dict[Union[Enum, str], bool]) -> dict:
    if not values:
        return {}

    include_values = [key.value if isinstance(key, Enum) else key for key, need in values.items() if need]
    exclude_values = [key.value if isinstance(key, Enum) else key for key, need in values.items() if not need]
    query = {}

    if include_values:
        query["$in"] = include_values

    if exclude_values:
        query["$nin"] = exclude_values

    return {name: query}
