# Архитектура (MVP)

## 1. Обзор
Приложение: FastAPI + шаблоны (Jinja2/HTMX опционально) + SQLite.

Цель архитектуры MVP:
- быстро получить рабочий инструмент,
- сохранить читаемость,
- оставить путь роста (PostgreSQL/Timescale, фоновые задачи, алерты).

## 2. Компоненты
- **API/Web layer (routers)**: принимает запросы, валидирует параметры.
- **Service layer**:
  - import_service: разбор CSV, валидация, статистика
  - dashboard_service: агрегации
  - export_service: выгрузка выборки в CSV
- **Data layer**:
  - SQLAlchemy модели
  - SessionLocal
  - репозитории (опционально, если усложнится)

## 3. Модель данных
### ImportRun
- id (PK)
- started_at (datetime tz)
- filename (string)
- inserted (int)
- skipped (int)
- errors (int)

### Event
- id (PK)
- timestamp (datetime tz)
- source (string, index)
- level (string, index)
- message (text)
- metric_value (float, nullable)
- tag (string, nullable, index)
- import_run_id (FK -> import_runs.id)

Связь:
- ImportRun 1—* Event

## 4. Поток данных
1) Пользователь загружает CSV.
2) import_service:
   - проверяет header
   - парсит строки
   - пишет события в БД
   - считает inserted/skipped/errors
3) events:
   - читает из БД
   - применяет фильтры
4) dashboard:
   - агрегации по events
5) export:
   - выборка по фильтрам
   - потоковая отдача CSV

## 5. Рост после MVP (направления)
- SQLite -> PostgreSQL/TimescaleDB
- Live ingest (socket/API) + очередь (Celery/RQ)
- Алерты по правилам (threshold/regex)
- Роли/авторизация
- Нормализация источников (таблица sources)