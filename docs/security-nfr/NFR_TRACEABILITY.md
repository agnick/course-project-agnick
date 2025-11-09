# Матрица трассировки NFR ↔ Stories/Tasks

| NFR ID | Story/Task                                                         | Приоритет | Release/Milestone |
|--------|--------------------------------------------------------------------|-----------|-------------------|
| NFR-01 | AUTH-01 — Включить проверку X-Auth-Token на всех `/wishes*`        | High      | 2025.10           |
| NFR-02 | API-04 — Обработчик RequestValidationError → 422 JSON              | Medium    | 2025.10           |
| NFR-03 | API-06 — Единый формат ошибок `{error:{code,message}}`             | High      | 2025.10           |
| NFR-04 | PERF-03 — Нагрузочный тест `/wishes/sorted` 30 RPS/5m              | Medium    | 2025.10           |
| NFR-05 | CI-02 — SCA (Dependabot/Snyk) и SLA ≤ 7 дней                       | High      | 2025.10           |
| NFR-06 | CORE-07 — Тесты атомарности/консистентности `_DB`                  | High      | 2025.10           |
| NFR-07 | LOG-03 — Маскирование/отсутствие PII в логах                       | Medium    | 2025.10           |
| NFR-08 | MON-01 — Метрика latency для `/health`                             | Low       | 2025.10           |
| NFR-09 | AUTH-11 — Регистрация/хранение паролей (Argon2id t=3,m=256MiB,p=1) | High      | 2025.11           |
| NFR-10 | AUTH-12 — JWT (HS256) с TTL ≤ 60 мин + ревокация                   | High      | 2025.11           |
