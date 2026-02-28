from __future__ import annotations


def _seed_data(client, sample_csv):
    response = client.post("/import", files={"file": ("events.csv", sample_csv, "text/csv")})
    assert response.status_code == 200


def test_ui_dashboard_page_loads(client, sample_csv):
    _seed_data(client, sample_csv)

    response = client.get("/ui/dashboard")

    assert response.status_code == 200
    assert "Ops Mini Dashboard" in response.text
    assert "Top sources" in response.text
    assert "theme-toggle" in response.text
    assert "/static/js/theme.js" in response.text


def test_ui_events_accepts_datetime_local_inputs(client, sample_csv):
    _seed_data(client, sample_csv)

    response = client.get(
        "/ui/events",
        params={
            "start": "2026-02-28T21:09",
            "end": "2026-02-28T21:10",
            "level": "ERROR",
        },
    )

    assert response.status_code == 200
    assert "Write timeout while flushing chunk" in response.text


def test_ui_events_table_partial_renders_rows(client, sample_csv):
    _seed_data(client, sample_csv)

    response = client.get("/ui/events/table", params={"level": "ERROR"})

    assert response.status_code == 200
    assert "Write timeout while flushing chunk" in response.text
    assert "<table>" in response.text


def test_ui_import_page_handles_file_upload(client, sample_csv):
    response = client.post(
        "/ui/import",
        files={"file": ("events.csv", sample_csv, "text/csv")},
    )

    assert response.status_code == 200
    assert "Импорт завершен" in response.text
    assert "events.csv" in response.text


def test_ui_import_page_supports_pagination(client, sample_csv):
    client.post("/import", files={"file": ("first.csv", sample_csv, "text/csv")})
    client.post("/import", files={"file": ("second.csv", sample_csv, "text/csv")})
    client.post("/import", files={"file": ("third.csv", sample_csv, "text/csv")})

    response = client.get("/ui/import", params={"limit": 1, "offset": 1})

    assert response.status_code == 200
    assert "second.csv" in response.text


def test_ui_pages_load_with_empty_db(client):
    """Все страницы UI должны возвращать 200 даже при пустой базе данных."""
    assert client.get("/ui/dashboard").status_code == 200
    assert client.get("/ui/events").status_code == 200
    assert client.get("/ui/events/table").status_code == 200
    assert client.get("/ui/import").status_code == 200


def test_ui_events_no_false_next_page(client, sample_csv):
    """Если событий ровно limit — ссылки «вперёд» быть не должно."""
    _seed_data(client, sample_csv)  # 3 события

    # Запрашиваем ровно 3 — это последняя страница
    response = client.get("/ui/events", params={"limit": 3, "offset": 0})

    assert response.status_code == 200
    # Следующей страницы нет — ссылка не должна появляться
    assert "offset=3" not in response.text
