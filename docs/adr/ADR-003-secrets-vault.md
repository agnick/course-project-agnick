# ADR-003: Управление секретами через Vault
Дата: 2025-10-19
Статус: Accepted

## Context
На данный момент тестовые токены (`USERS`) хранятся в коде (`app/core/auth.py`).
В продакшен‑среде это нарушает **NFR‑05** и повышает риск утечки (**R7**, **R8**).
Необходимо перейти на безопасное централизованное хранение секретов в **HashiCorp Vault** с автоматической ротацией и запретом логирования.

## Decision
1. Секреты (`X‑Auth‑Token`, JWT ключи) хранятся в Vault под `secret/wishlist/tokens`.
2. Приложение получает их через Vault API при старте контейнера.
3. Добавляется промежуточный слой `VaultSettings`:
```python
import hvac

class VaultSettings:
    def __init__(self, url: str, token: str):
        self.client = hvac.Client(url=url, token=token)

    def get_token_map(self) -> dict[str,str]:
        return self.client.secrets.kv.v2.read_secret_version(path="wishlist/tokens")["data"]["data"]
```
4. Логи фильтруют токены (`MaskPIIFilter`) согласно **NFR‑07**.

## Alternatives
| Вариант             | Плюсы                  | Минусы                          |
|---------------------|------------------------|---------------------------------|
| Хранить в .env      | Простота               | Риск утечки в CI                |
| AWS Secrets Manager | Масштабируемо          | Vendor lock‑in                  |
| Vault self‑hosted   | Контроль, безопасность | Требует настройку ACL и токенов |

## Consequences
- (+) Централизованная ротация (раз в 30 дней).
- (+) Исключение секретов из кода.
- (–) Дополнительная зависимость от Vault‑сервиса.

## Security impact
- STRIDE: **I — Information Disclosure**, **E — Elevation of Privilege**
- Threats: **R7, R8**
- NFR: **NFR‑05, NFR‑07**
- KPI: 0 секретов в коде, SLA устранения CVE ≤ 7 дней.

## Rollout plan
1. Добавить клиент `VaultSettings` в `app/core/secrets.py`.
2. Настроить Vault‑токен в CI через masked secret.
3. Проверить отсутствие `token` в логах (`test_logs_do_not_contain_tokens`).
4. В будущем — миграция `USERS` → Vault storage.

## Links
- `app/core/auth.py`
- `RISKS.md: R7, R8`
- `STRIDE.md: F5, F6`
- `NFR.md: NFR‑05, NFR‑07`
- `tests/test_vault_integration.py`
