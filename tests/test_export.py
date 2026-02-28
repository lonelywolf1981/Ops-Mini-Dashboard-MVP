from __future__ import annotations

from app.services.export_service import MAX_EXPORT_ROWS


def seed_for_export(client, sample_csv):
    response = client.post(
        "/import",
        files={"file": ("events.csv", sample_csv, "text/csv")},
    )
    assert response.status_code == 200


def test_export_returns_csv_header(client, sample_csv):
    seed_for_export(client, sample_csv)

    response = client.get("/events/export.csv")

    assert response.status_code == 200
    lines = response.text.strip().splitlines()
    assert lines[0] == "timestamp,source,level,message,metric_value,tag"


def test_export_respects_level_filter(client, sample_csv):
    seed_for_export(client, sample_csv)

    response = client.get("/events/export.csv", params={"level": "ERROR"})

    assert response.status_code == 200
    lines = response.text.strip().splitlines()
    assert len(lines) == 2  # заголовок + 1 строка
    assert ",ERROR," in lines[1]


def test_export_row_limit_constant_is_defined():
    """MAX_EXPORT_ROWS должен быть определён и иметь разумное значение."""
    assert isinstance(MAX_EXPORT_ROWS, int)
    assert MAX_EXPORT_ROWS > 0
