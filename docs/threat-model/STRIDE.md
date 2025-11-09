# STRIDE-анализ угроз для сервиса Wishlist

| Поток / Элемент              | Угроза (STRIDE)                              | Риск | Контроль / Мера защиты                                                | Ссылка на NFR  | Проверка / Артефакт                                    |
|------------------------------|----------------------------------------------|------|-----------------------------------------------------------------------|----------------|--------------------------------------------------------|
| **F1: HTTPS /wishes**        | **S: Spoofing (подделка клиента)**           | R1   | Проверка `X-Auth-Token`, HTTP 401 для неавторизованных                | NFR-01         | e2e тест `test_unauthorized_access_returns_401`        |
| **F1: HTTPS /wishes**        | **T: Tampering (модификация запроса)**       | R2   | Только HTTPS, Pydantic-валидация тела запроса                         | NFR-02, NFR-04 | Pytest контракт-тесты, FastAPI validation layer        |
| **F2: Проверка токена**      | **R: Repudiation (отказ от действия)**       | R3   | Логирование ошибок без PII; трассировка по request-id                 | NFR-03, NFR-07 | Логи CI + аудит ошибок                                 |
| **F3: CRUD /wishes**         | **T: Tampering (повреждение данных)**        | R4   | CRUD атомарны; при сбое транзакции не изменяют состояние              | NFR-06         | Unit-тест `test_nfr06_db_consistency_on_failed_put...` |
| **F3: CRUD /wishes**         | **I: Information Disclosure (утечка)**       | R5   | Доступ только к своим записям; фильтрация по owner                    | NFR-01, NFR-06 | e2e + code review                                      |
| **F4: Metrics /health**      | **D: Denial of Service (перегрузка)**        | R6   | `/health` оптимизирован, p95 ≤ 100 мс, без доступа к БД               | NFR-08         | Pytest нагрузочный тест latency                        |
| **F5: Logs /errors**         | **I: Information Disclosure (PII)**          | R7   | Маскирование токенов и паролей в логах                                | NFR-07         | Лог-анализ + паттерн-тесты                             |
| **F6: SCA Reports**          | **T: Tampering (подмена отчёта SCA)**        | R8   | Dependabot и Snyk подписаны; CI блокирует merge при CVE High/Critical | NFR-05         | GitHub CI Security Dashboard                           |
| **F7: Export / Import JSON** | **I: Information Disclosure**                | R9   | Проверка владельца, сериализация только своих записей                 | NFR-01, NFR-02 | e2e тест на импорт/экспорт                             |
| **F7: Export / Import JSON** | **T: Tampering (загрузка вредоносных JSON)** | R10  | Pydantic схема + ограничение размера запроса                          | NFR-02         | Unit-тест валидации                                    |
| **F8: Response (JSON)**      | **R: Repudiation**                           | R11  | Единый формат ошибок `{error:{code,message}}`, без stacktrace         | NFR-03         | Pytest `test_error_format_is_uniform`                  |
| **DB / In-Memory _DB**       | **E: Elevation of Privilege**                | R12  | Нет внешнего доступа к _DB; CRUD через AuthN/AuthZ слой               | NFR-01, NFR-06 | Code review + e2e                                      |

---

## Обоснование исключений

- **Denial of Service (DoS)** для CI/CD-потоков (F6) не применим, т.к. операции выполняются офлайн.
- **Elevation of Privilege** для `Uvicorn Logger` и `Monitoring System` не применим, так как нет интерфейсов приёма входных данных.
