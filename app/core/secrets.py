from __future__ import annotations

import json
import os
from typing import Dict

_DEFAULT_TOKEN_MAP: Dict[str, str] = {
    "token123": "alice",
    "token456": "bob",
}


class SecretsProvider:
    def __init__(self, env_json_var: str = "VAULT_TOKEN_MAP_JSON"):
        self._env_json_var = env_json_var
        self._cache: Dict[str, str] | None = None

    def get_token_map(self) -> Dict[str, str]:
        if self._cache is not None:
            return self._cache
        raw = os.getenv(self._env_json_var)
        if raw:
            try:
                data = json.loads(raw)
                if isinstance(data, dict) and all(
                    isinstance(k, str) and isinstance(v, str) for k, v in data.items()
                ):
                    self._cache = data
                    return self._cache
            except Exception:
                pass
        self._cache = dict(_DEFAULT_TOKEN_MAP)
        return self._cache


_provider = SecretsProvider()


def get_token_map() -> Dict[str, str]:
    return _provider.get_token_map()
