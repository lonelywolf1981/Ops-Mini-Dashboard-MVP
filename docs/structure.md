ops-mini-dashboard/
├─ app/
│  ├─ main.py               # сборка приложения, подключение роутеров
│  ├─ db.py                 # engine и SessionLocal
│  ├─ models.py             # ORM-модели: ImportRun, Event
│  ├─ dependencies.py       # get_db для Depends(get_db)
│  ├─ routers/
│  │  ├─ dashboard.py       # GET /dashboard, GET /dashboard/top-sources
│  │  ├─ events.py          # GET /events, GET /events/export.csv
│  │  ├─ import_data.py     # POST /import, GET /imports
│  │  └─ web.py             # GET|POST /ui/* (server-side UI)
│  ├─ services/
│  │  ├─ import_service.py  # парсинг CSV, валидация, статистика
│  │  ├─ events_service.py  # фильтры, пагинация, список источников
│  │  ├─ dashboard_service.py # агрегации: total, by_level, by_day, top
│  │  └─ export_service.py  # потоковая выгрузка CSV (до 5000 строк)
│  ├─ templates/
│  │  ├─ base.html
│  │  ├─ dashboard.html
│  │  ├─ events.html
│  │  ├─ events_table.html  # HTMX partial для таблицы событий
│  │  └─ import.html
│  └─ static/
│     ├─ css/app.css
│     └─ js/theme.js        # переключение светлой/тёмной темы
├─ tests/
│  ├─ conftest.py           # фикстуры: db_session, client, sample_csv
│  ├─ test_import.py
│  ├─ test_events.py
│  ├─ test_export.py
│  ├─ test_dashboard.py
│  └─ test_web_ui.py
├─ data/
│  └─ sample_events.csv     # демо-данные (20 событий)
├─ docs/
│  ├─ tz.md
│  ├─ architecture.md
│  ├─ API.md
│  ├─ data-format.md
│  ├─ decision-log.md
│  ├─ testplan.md
│  ├─ project-defense.md
│  ├─ roadmap.md
│  └─ structure.md          # этот файл
├─ screenshots/
├─ .github/
│  └─ workflows/
│     └─ ci.yml             # CI: ruff + pytest на каждый push
├─ .gitattributes
├─ .gitignore
├─ requirements.txt
└─ ReadMe.md
