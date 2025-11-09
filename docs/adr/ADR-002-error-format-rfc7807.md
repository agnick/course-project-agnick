# ADR-002: Формат ошибок RFC 7807 и маскирование деталей
Дата: 2025-10-19
Статус: Accepted

## Context
В текущем коде (`app/core/errors.py`) все ошибки возвращаются в формате `{error:{code,message}}`.
Это реализует базовую унификацию (**NFR‑03**) и предотвращает утечку стеков.
Для улучшения трассировки и соответствия стандарту планируется переход на RFC 7807 с `correlation_id`.
Это также закрывает риск **R2** (Tampering) и **R3** (Repudiation) — теперь каждая ошибка имеет уникальный ID.

## Decision
Добавить вспомогательную функцию `problem()` для формирования RFC 7807‑ответов:
```python
from uuid import uuid4
from starlette.responses import JSONResponse

def problem(status: int, title: str, detail: str, type_: str = "about:blank"):
    cid = str(uuid4())
    payload = {"type": type_, "title": title, "status": status, "detail": detail, "correlation_id": cid}
    return JSONResponse(payload, status_code=status)
```
Формат будет использоваться во всех хэндлерах FastAPI, начиная с 422 и 401.

## Alternatives
| Вариант                     | Плюсы           | Минусы              |
|-----------------------------|-----------------|---------------------|
| Оставить старый JSON‑формат | Совместимость   | Нет correlation_id  |
| Логировать traceback        | Простая отладка | Утечка PII          |
| Использовать Sentry SDK     | Централизация   | Внешняя зависимость |

## Consequences
- (+) Улучшена трассируемость ошибок.
- (+) Нет утечек деталей реализации.
- (–) Изменение схемы API потребует обновить тесты клиентов.

## Security impact
- STRIDE: **I — Information Disclosure**, **R — Repudiation**
- Threats: **R2, R3**
- NFR: **NFR‑03, NFR‑07**
- KPI: 100% ошибок содержат correlation_id; 0 stacktrace в ответах.

## Rollout plan
1. Добавить `problem()` в `app/core/errors.py`.
2. Заменить все JSON‑ответы на RFC 7807‑формат.
3. Проверить тест `test_rfc7807_contract` и аудит логов CI.

## Links
- `app/core/errors.py`
- `RISKS.md: R2, R3`
- `STRIDE.md: F2, F8`
- `NFR.md: NFR‑03, NFR‑07`
- `tests/test_nfr.py::test_invalid_title_returns_422`
