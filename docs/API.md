# API (MVP)

Базовый набор эндпоинтов (можно сначала отдавать JSON, UI добавить позже).

## 1) Dashboard
### GET /dashboard
Возвращает:
- total
- by_level {INFO: n, WARN: n, ERROR: n}
- unique_sources
- by_day [{day, count}]
- latest [..last 20 events..]

## 2) Events
### GET /events
Query:
- level: INFO|WARN|ERROR (optional)
- source: string (optional)
- q: string (optional, substring in message)
- start: ISO timestamp (optional)
- end: ISO timestamp (optional)
- limit: 1..500 (default 100)
- offset: >=0 (default 0)

Response: список событий.

## 3) Export
### GET /events/export.csv
Query: те же, что /events (без limit/offset), ограничение: 5000 строк.

Response: text/csv.

## 4) Import
### POST /import
Form-data:
- file: UploadFile (.csv или .json)

Поддерживаемые форматы:
- `.csv` — строгий заголовок `timestamp,source,level,message,metric_value,tag`
- `.json` — массив объектов с теми же полями

Response:
- import_run_id
- filename
- inserted
- skipped
- errors

## 5) Import history (v0.2)
### GET /imports
Query:
- limit: 1..200 (default 50)
- offset: >=0 (default 0)

Response: список запусков импорта (`ImportRun`) в порядке новых к старым:
- id
- started_at (ISO timestamp)
- filename
- inserted
- skipped
- errors

## 6) Top sources (v0.2)
### GET /dashboard/top-sources
Query:
- limit: 1..50 (default 5)

Response:
- ERROR: [{source, count}, ...]
- WARN: [{source, count}, ...]

Источник и count агрегируются по событиям соответствующего уровня.

## 7) Web UI (v0.2)

UI реализован как server-side rendered страницы на Jinja.

### GET /ui/dashboard
- Показывает метрики `/dashboard` и top-sources.

### GET /ui/events
- Показывает таблицу событий, фильтры и пагинацию.
- Поддерживает удобные local datetime inputs для диапазона (`start/end`).

### GET /ui/events/table
- Возвращает HTML-фрагмент таблицы событий и pager для HTMX.
- Используется страницей `/ui/events` для частичного обновления таблицы без full reload.

### GET /ui/import
- Страница загрузки CSV + таблица последних импортов.

### POST /ui/import
- Загружает CSV из формы и показывает результат импорта.
