# План тестирования (ручной) — MVP

## 1. Запуск
- [ ] Приложение стартует по инструкции README.
- [ ] /docs (OpenAPI) доступен.

## 2. Импорт
### 2.1. Успешный импорт
- [ ] POST /import с `sample_events.csv` возвращает inserted > 0, errors = 0 (или минимальные).
- [ ] /events показывает импортированные события.

### 2.2. Неверный заголовок
- [ ] CSV с неправильным header -> 400 и понятная ошибка.

### 2.3. Неверный timestamp
- [ ] Строка с timestamp `BAD` -> увеличивает errors.

### 2.4. Неверный level
- [ ] level = `DEBUG` -> skipped.

## 3. Events (фильтры)
- [ ] /events?level=ERROR возвращает только ERROR.
- [ ] /events?source=sensor-temp-01 возвращает только этот source.
- [ ] /events?q=timeout находит строку с message содержащей timeout.
- [ ] /events?start=...&end=... ограничивает диапазон.

## 4. Dashboard
- [ ] total совпадает с количеством строк в БД.
- [ ] by_level соответствует выборке /events.
- [ ] unique_sources соответствует distinct(source).
- [ ] latest возвращает 20 последних по timestamp desc.

## 5. Export
- [ ] /events/export.csv выдаёт CSV с заголовком.
- [ ] export с фильтром level=ERROR выдаёт только ERROR.

## 6. Import history (v0.2)
- [ ] /imports возвращает список запусков импорта от новых к старым.
- [ ] limit/offset на /imports работают корректно.

## 7. Top sources (v0.2)
- [ ] /dashboard/top-sources возвращает блоки ERROR и WARN.
- [ ] В каждом блоке источники отсортированы по убыванию count.
- [ ] Параметр limit ограничивает количество элементов в каждом блоке.

## 8. Web UI (v0.2)
- [ ] /ui/dashboard открывается и показывает метрики.
- [ ] /ui/events открывается и отображает таблицу событий.
- [ ] Фильтры /ui/events принимают `datetime-local` значения start/end.
- [ ] /ui/events/table отдает HTML-фрагмент таблицы для HTMX.
- [ ] /ui/import открывается и принимает загрузку CSV.
- [ ] После POST /ui/import отображается статистика inserted/skipped/errors.
