# Ops Mini Dashboard (MVP)

Внутренний веб-дашборд для инженеров/лабораторий/техслужбы: импорт событий из CSV и просмотр сводки, фильтрация, базовая визуализация и экспорт.

## Зачем
- Быстро получить прозрачность по событиям/ошибкам из разрозненных источников (оборудование, сервисы, тестовые стенды).
- Упростить анализ: "что происходило", "где ошибки", "какие источники шумят".

## Возможности MVP
- Импорт CSV с событиями.
- Список событий с фильтрами (дата, source, level, поиск по message).
- Dashboard со сводкой и 1–2 графиками.
- Экспорт отфильтрованной выборки в CSV.

## Дополнения v0.2
- История импортов: `GET /imports`.
- Топ источников по проблемным уровням: `GET /dashboard/top-sources`.
- Минимальный web UI:
  - `GET /ui/dashboard`
  - `GET /ui/events`
  - `GET /ui/import`
- Удобный выбор диапазона времени в UI (`datetime-local` контролы).
- HTMX-подгрузка таблицы событий без полной перезагрузки страницы (`/ui/events/table`).

## Не входит в MVP
- Авторизация/роли.
- Real-time стриминг (WebSocket).
- Алерты/уведомления.
- Сложный фронтенд (SPA).

## Быстрый старт (локально)
1) Создать виртуальное окружение:
   - `python -m venv .venv`
   - Windows: `.venv\Scripts\activate`
2) Установить зависимости:
   - `python -m pip install --upgrade pip`
   - `pip install fastapi "uvicorn[standard]" sqlalchemy pytest ruff mypy httpx python-multipart jinja2`
3) Запустить API:
   - `uvicorn app.main:app --reload`

После запуска:
- Swagger/OpenAPI: `http://127.0.0.1:8000/docs`
- Web UI Dashboard: `http://127.0.0.1:8000/ui/dashboard`
- Web UI Events: `http://127.0.0.1:8000/ui/events`
- Web UI Import: `http://127.0.0.1:8000/ui/import`

Точные требования см. `docs/tz.md`.

## Демо-данные
Формат CSV описан в `docs/data-format.md`.
Пример файла: `data/sample_events.csv`.

## Документация
- ТЗ: `docs/tz.md`
- Архитектура: `docs/architecture.md`
- API: `docs/API.md`
- Формат данных: `docs/data-format.md`
- План тестирования: `docs/testplan.md`
- Лог решений: `docs/decision-log.md`
- Защита проекта: `docs/project-defense.md`
- Roadmap: `docs/roadmap.md`
