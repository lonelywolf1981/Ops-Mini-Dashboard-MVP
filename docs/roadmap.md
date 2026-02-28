# Roadmap

## MVP (v0.1)
- [x] Импорт CSV (строгий header)
- [x] Хранение (SQLite)
- [x] Events (фильтры + пагинация)
- [x] Dashboard (сводка + 1–2 графика)
- [x] Export CSV
- [x] Документация (TZ/arch/api/tests/decisions/defense)

## v0.2
- [x] UI на Jinja/HTMX (если MVP был JSON-only)
- [x] Выбор диапазона дат удобным контролом
- [x] Список импортов (ImportRun history)
- [x] Просмотр "топ источников" по ERROR/WARN

## v0.3
- PostgreSQL
- Bulk insert + ускорение импорта
- Теги и быстрые пресеты фильтров

## v1.0
- API ingest (не только CSV)
- Алерты по правилам (threshold/regex)
- Пользователи/роли
- Аудит действий
