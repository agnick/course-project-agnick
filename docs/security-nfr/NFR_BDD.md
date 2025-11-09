# BDD сценарии для Security NFR

## Feature: Защищённый доступ к API (NFR-01)
```
  Scenario: Без токена — 401
    Given клиент отправляет GET /wishes без заголовка X-Auth-Token
    When сервер обрабатывает запрос
    Then статус ответа = 401
    And тело содержит {"error":{"code":"http_error","message":"unauthorized"}}
```

---

## Feature: Валидация и единый формат ошибок (NFR-02, NFR-03)
```
  Scenario: Некорректный title возвращает 422 в едином JSON
    Given POST /wishes с title длиной > 50 символов
    When Pydantic валидирует тело запроса
    Then статус ответа = 422
    And тело содержит {"error":{"code":"validation_error", ...}}
```

---

## Feature: Производительность сортировки (NFR-04)
```
  Scenario: p95 /wishes/sorted ≤ 200 мс при 30 RPS
    Given stage окружение и нагрузка 30 RPS на /wishes/sorted
    When проводится 5-минутный тест
    Then p95 времени ответа ≤ 200 мс по отчёту нагрузочного теста
```

---

## Feature: Хранение паролей — Argon2id (NFR-09)
```
  Scenario: Пароль сохраняется как Argon2id с заданными параметрами
    Given пользователь регистрируется через /auth/register с валидным паролем
    When сервис сохраняет учётную запись
    Then в хранилище есть только Argon2id-хэш
    And параметры соответствуют t=3, m=256MiB, p=1
```

---

## Feature: TTL/JWT токенов (NFR-10)
```
  Scenario: Истёкший JWT отклоняется
    Given пользователь авторизовался и получил JWT с exp=60 мин
    And прошло 61 минута
    When клиент обращается к /wishes с этим токеном
    Then статус ответа = 401
    And тело содержит {"error":{"code":"http_error","message":"unauthorized"}}
```

---

## Negative Scenario: Консистентность `_DB` при сбое (NFR-06)
```
  Scenario: Данные не повреждаются при исключении
    Given существует wish владельца alice
    And во время update_wish происходит исключение
    When операция прерывается
    Then в _DB["wishes"] нет дубликатов или битых записей
```
