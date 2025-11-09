# Data Flow Diagram

## 1. Уровень 1 — Контекстная диаграмма

```mermaid
flowchart LR
  U[Пользователь] -->|F1: HTTPS /wishes, /health| API[Wishlist API Service]

  subgraph Edge[TrustBoundary_Edge]
    API -->|F2: Проверка токена и валидация| APP[Business Logic Layer]
  end

  subgraph Core[TrustBoundary_Core]
    APP -->|F3: CRUD /wishes| DB[(In-Memory _DB)]
    APP -->|F4: Metrics /health| MON[(Monitoring System)]
    APP -->|F5: Logs /errors| LOG[(Uvicorn Logger)]
  end

  subgraph CI[TrustBoundary_CI_CD]
    DEP[Dependabot / Snyk] -->|F6: SCA Reports| PIPE[CI Pipeline]
  end

  U -->|F7: Export / Import JSON| API
  API -->|F8: Response JSON| U
```

---

## 2. Пояснения к потокам

| Поток  | Описание                                            | Протокол / Механизм    | Применимые NFR | Потенциальные угрозы (STRIDE)     |
|--------|-----------------------------------------------------|------------------------|----------------|-----------------------------------|
| **F1** | Внешний запрос клиента к API (`/wishes`, `/health`) | HTTPS (TLS 1.2+)       | NFR-01, NFR-03 | Spoofing, Tampering               |
| **F2** | Проверка токена и валидация данных (Pydantic)       | FastAPI internal call  | NFR-02, NFR-03 | Tampering, Information Disclosure |
| **F3** | CRUD-операции с `_DB`                               | Внутренний Python API  | NFR-06         | Tampering, Repudiation            |
| **F4** | Отправка метрик `/health`                           | HTTP GET               | NFR-08         | Denial of Service                 |
| **F5** | Логирование ошибок и запросов                       | stdout (uvicorn.error) | NFR-07         | Information Disclosure            |
| **F6** | Отчёты анализа зависимостей                         | GitHub API / Snyk      | NFR-05         | Elevation of Privilege            |
| **F7** | Экспорт / импорт JSON-бэкапов                       | HTTPS                  | NFR-04         | Tampering, DoS                    |
| **F8** | Ответ API клиенту (JSON)                            | HTTPS                  | NFR-03         | Information Disclosure            |

---

## 3. Уровень 2 — Детализированный поток внутри Wishlist API

```mermaid
flowchart TD
  subgraph Edge[Trust Boundary: Edge / API Layer]
    CL[Client X-Auth-Token] -->|F1: HTTPS POST /wishes| VAL[Validation + Auth Middleware]
    VAL -->|F2: 422 JSON при ошибках| CL
    CL -->|F3: GET /wishes/sorted| CTRL[Sorting Controller]
  end

  subgraph Core[Trust Boundary: Core / Business Logic]
    CTRL -->|F4: CRUD операции| DB[(In-Memory _DB)]
    CTRL -->|F5: Метрики health| HEALTH[/health endpoint/]
    CTRL -->|F6: Логирование ошибок| LOG[(Uvicorn Logger)]
  end

  subgraph CI[Trust Boundary: CI/CD Pipeline]
    DEP[Dependabot / Snyk] -->|F7: Анализ зависимостей SCA| REPORT[SCA Report JSON]
    REPORT -->|F8: Уведомление разработчика| DEV[Developer]
  end
```

---

## 4. Trust Boundaries

| Граница         | Компоненты                                        | Потоки | Меры защиты                                         |
|-----------------|---------------------------------------------------|--------|-----------------------------------------------------|
| **Edge Layer**  | FastAPI маршруты `/wishes`, `/health`, middleware | F1–F3  | Проверка `X-Auth-Token`, HTTPS, Pydantic validation |
| **Core Layer**  | CRUD-логика, `_DB`, логирование, метрики          | F4–F6  | Изоляция данных, маскирование PII, fault tolerance  |
| **CI/CD Layer** | Dependabot, Snyk, GitHub Actions                  | F7–F8  | Контроль зависимостей, SLA на устранение CVE        |

---

## 5. Соответствие с NFR и STRIDE

| Поток / Компонент | STRIDE категория                    | Контроль (связанный NFR)     |
|-------------------|-------------------------------------|------------------------------|
| F1, F2            | **S** Spoofing / **T** Tampering    | `NFR-01`, `NFR-02`, `NFR-03` |
| F3, F4            | **T** Tampering / **R** Repudiation | `NFR-06`, `NFR-08`           |
