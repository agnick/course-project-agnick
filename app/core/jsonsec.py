from __future__ import annotations

import json

MAX_JSON_BYTES = 2_000_000


class JsonTooLargeError(ValueError):
    pass


def safe_json_loads(raw: bytes) -> dict:
    """
    Безопасный парсер JSON:
    - Лимит на размер тела (байты)
    - parse_float=str исключает двоичную неточность float
    Возвращает dict верхнего уровня.
    """
    if len(raw) > MAX_JSON_BYTES:
        raise JsonTooLargeError("json body too large")

    data = json.loads(raw, parse_float=str)
    if not isinstance(data, dict):
        raise ValueError("root must be an object")
    return data
