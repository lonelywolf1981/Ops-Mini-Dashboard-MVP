# Project Defense (MVP)

## Что проект делает за 30 секунд

`Ops Mini Dashboard` — это внутренний инструмент для загрузки событий из CSV,
их хранения в SQLite и быстрого анализа через API.

Пользователь:
1. Загружает CSV в `POST /import`.
2. Получает статистику импорта (`inserted/skipped/errors`).
3. Смотрит историю запусков импорта в `GET /imports`.
4. Смотрит события в `GET /events` с фильтрами.
5. Смотрит сводные метрики в `GET /dashboard`.
6. Смотрит топ источников по `ERROR/WARN` в `GET /dashboard/top-sources`.
7. Экспортирует отфильтрованный набор через `GET /events/export.csv`.

## Ключевые сущности

### ImportRun
- Один запуск импорта файла.
- Хранит имя файла, время старта и итоговые счетчики:
  `inserted`, `skipped`, `errors`.

### Event
- Одна запись события с полями:
  `timestamp`, `source`, `level`, `message`, `metric_value`, `tag`.
- Каждое событие связано с `import_run_id`.

## Где находится основная логика

### API слой (routers)
- `app/routers/import_data.py` — endpoint импорта.
- `app/routers/events.py` — список событий и CSV-экспорт.
- `app/routers/dashboard.py` — агрегированные метрики + top-sources.
- `app/routers/web.py` — server-side web UI (`/ui/dashboard`, `/ui/events`, `/ui/import`).

Роутеры намеренно «тонкие»: принимают параметры и вызывают сервисы.

### Service слой
- `app/services/import_service.py`
  - Проверяет расширение `.csv`.
  - Проверяет строгий header в точном порядке.
  - Парсит строки, считает `inserted/skipped/errors`.
  - Отдает историю импортов (`/imports`) с пагинацией.
- `app/services/events_service.py`
  - Валидирует `level` и timestamp-параметры.
  - Строит единые фильтры для выборок.
  - Формирует JSON-ответ `/events`.
- `app/services/dashboard_service.py`
  - Считает `total`, `by_level`, `unique_sources`, `by_day`, `latest`.
  - Считает top источников по `ERROR` и `WARN`.
- `app/services/export_service.py`
  - Делает выборку по тем же фильтрам, что `/events`.
  - Отдает CSV потоково, лимит до 5000 строк.

### Data слой
- `app/models.py` — SQLAlchemy модели `ImportRun` и `Event`.
- `app/db.py` — engine и session factory.
- `app/dependencies.py` — `get_db` для DI в FastAPI.

## Как читать код по модулям (для новичка)

Рекомендуемый порядок чтения:

1. `app/main.py`
   - Понять, как собирается приложение и подключаются роутеры.
2. `app/routers/*.py`
   - Увидеть HTTP-контракт: какие URL есть и какие параметры принимаются.
3. `app/services/*.py`
   - Разобрать бизнес-логику: валидация, фильтры, импорт, агрегаты, экспорт.
4. `app/models.py`
   - Сопоставить код с сущностями `ImportRun` и `Event`.
5. `tests/*.py`
   - Проверить, какие сценарии считаются правильными и какие ошибки ожидаются.

Мини-правило: если нужно менять поведение endpoint, сначала правим service,
потом роутер (если требуется новый параметр), потом тесты.

## Что делает каждый модуль кратко

- `app/routers/import_data.py`: принимает CSV-файл и передает его в import service.
- `app/routers/events.py`: отдает список событий и CSV-экспорт.
- `app/routers/dashboard.py`: отдает агрегированную сводку и top-sources.
- `app/services/import_service.py`: строгая валидация CSV + подсчет статистики.
- `app/services/events_service.py`: единая фильтрация (`level/source/q/start/end`) и JSON-формат.
- `app/services/export_service.py`: CSV-стрим с теми же фильтрами, что `/events`.
- `app/services/dashboard_service.py`: расчеты `total/by_level/unique_sources/by_day/latest` и top-sources.
- `tests/conftest.py`: тестовая SQLite in-memory и dependency override для FastAPI.
- `app/templates/*.html`: UI-страницы для dashboard/events/import.
- `app/static/css/app.css`: стили UI.

## Ограничения MVP

- База данных SQLite (без продвинутого масштабирования).
- Нет авторизации/ролей и мульти-тенантности.
- Нет real-time ingest и алертинга.
- Нет сложной аналитики/ML-аномалий.

Эти ограничения соответствуют `docs/tz.md` и `docs/roadmap.md`.

## Что улучшить первым

1. Добавить UI (Jinja/HTMX) поверх текущего API.
2. Ввести миграции БД (Alembic).
3. Перейти на PostgreSQL при росте нагрузки.
4. Добавить UI-экран истории импортов (backend endpoint уже есть).
5. Увеличить покрытие тестами (больше edge-cases и property-based проверки импорта).

## Практика (что делать руками)

1. Добавить фильтр `tag` в `/events`:
   - расширить `build_event_filters(...)` в `app/services/events_service.py`;
   - пробросить query-параметр в `app/routers/events.py`;
   - добавить тест в `tests/test_events.py`.
2. Сделать UI-экран истории импортов:
   - получить данные из `GET /imports`;
   - добавить пагинацию limit/offset в интерфейсе;
   - показать колонки filename/inserted/skipped/errors.
3. Проверить формат ошибок:
   - bad timestamp в query должен давать понятный `400`.
