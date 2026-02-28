from __future__ import annotations

from app.services.import_service import MAX_UPLOAD_BYTES


def test_import_success(client, sample_csv):
    response = client.post(
        "/import",
        files={"file": ("events.csv", sample_csv, "text/csv")},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["inserted"] == 3
    assert payload["skipped"] == 0
    assert payload["errors"] == 0


def test_import_rejects_invalid_header_order(client):
    csv_content = (
        "source,timestamp,level,message,metric_value,tag\n"
        "sensor-temp-01,2026-02-28T21:06:00+05:00,INFO,Temperature reading,3.125,temp\n"
    )

    response = client.post(
        "/import",
        files={"file": ("events.csv", csv_content, "text/csv")},
    )

    assert response.status_code == 400
    assert "CSV header must be exactly" in response.json()["detail"]


def test_import_counts_timestamp_errors(client):
    csv_content = (
        "timestamp,source,level,message,metric_value,tag\n"
        "BAD,sensor-temp-01,INFO,Temperature reading,3.125,temp\n"
    )

    response = client.post(
        "/import",
        files={"file": ("events.csv", csv_content, "text/csv")},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["inserted"] == 0
    assert payload["errors"] == 1


def test_import_skips_invalid_level(client):
    csv_content = (
        "timestamp,source,level,message,metric_value,tag\n"
        "2026-02-28T21:06:00+05:00,sensor-temp-01,DEBUG,Temperature reading,3.125,temp\n"
    )

    response = client.post(
        "/import",
        files={"file": ("events.csv", csv_content, "text/csv")},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["inserted"] == 0
    assert payload["skipped"] == 1
    assert payload["errors"] == 0


def test_imports_history_returns_latest_first(client, sample_csv):
    first = client.post(
        "/import",
        files={"file": ("first.csv", sample_csv, "text/csv")},
    )
    second = client.post(
        "/import",
        files={"file": ("second.csv", sample_csv, "text/csv")},
    )

    assert first.status_code == 200
    assert second.status_code == 200

    first_id = first.json()["import_run_id"]
    second_id = second.json()["import_run_id"]

    response = client.get("/imports", params={"limit": 2, "offset": 0})

    assert response.status_code == 200
    payload = response.json()
    assert payload[0]["id"] == second_id
    assert payload[1]["id"] == first_id
    assert payload[0]["filename"] == "second.csv"


def test_imports_history_supports_pagination(client, sample_csv):
    client.post("/import", files={"file": ("one.csv", sample_csv, "text/csv")})
    two = client.post("/import", files={"file": ("two.csv", sample_csv, "text/csv")})
    client.post("/import", files={"file": ("three.csv", sample_csv, "text/csv")})

    assert two.status_code == 200
    second_id = two.json()["import_run_id"]

    page = client.get("/imports", params={"limit": 1, "offset": 1})

    assert page.status_code == 200
    rows = page.json()
    assert len(rows) == 1
    assert rows[0]["id"] == second_id


def test_import_rejects_oversized_file(client):
    """Файл больше MAX_UPLOAD_BYTES должен возвращать 413."""
    oversized = b"x" * (MAX_UPLOAD_BYTES + 1)

    response = client.post(
        "/import",
        files={"file": ("big.csv", oversized, "text/csv")},
    )

    assert response.status_code == 413
    assert "too large" in response.json()["detail"].lower()


def test_import_sanitizes_path_traversal_filename(client, sample_csv):
    """Имя файла с ../.. не должно сохраняться в БД как путь."""
    response = client.post(
        "/import",
        files={"file": ("../../etc/passwd.csv", sample_csv, "text/csv")},
    )

    assert response.status_code == 200
    # Должно сохраниться только имя файла без пути
    assert response.json()["filename"] == "passwd.csv"


# ---------------------------------------------------------------------------
# JSON import
# ---------------------------------------------------------------------------

def test_import_json_success(client, sample_json):
    response = client.post(
        "/import",
        files={"file": ("events.json", sample_json, "application/json")},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["inserted"] == 3
    assert payload["skipped"] == 0
    assert payload["errors"] == 0
    assert payload["filename"] == "events.json"


def test_import_json_numeric_metric_value(client):
    """JSON metric_value как число (не строка) должен корректно записываться."""
    data = (
        '[{"timestamp":"2026-02-28T21:06:00+05:00","source":"s","level":"INFO",'
        '"message":"m","metric_value":42.5,"tag":null}]'
    )
    response = client.post(
        "/import",
        files={"file": ("events.json", data, "application/json")},
    )

    assert response.status_code == 200
    assert response.json()["inserted"] == 1


def test_import_json_invalid_json(client):
    response = client.post(
        "/import",
        files={"file": ("events.json", "not valid json{", "application/json")},
    )

    assert response.status_code == 400
    assert "Invalid JSON" in response.json()["detail"]


def test_import_json_not_a_list(client):
    response = client.post(
        "/import",
        files={"file": ("events.json", '{"source":"s"}', "application/json")},
    )

    assert response.status_code == 400
    assert "list" in response.json()["detail"].lower()


def test_import_json_skips_invalid_level(client):
    data = (
        '[{"timestamp":"2026-02-28T21:06:00+05:00","source":"s","level":"DEBUG",'
        '"message":"m","metric_value":null,"tag":null}]'
    )
    response = client.post(
        "/import",
        files={"file": ("events.json", data, "application/json")},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["inserted"] == 0
    assert payload["skipped"] == 1


def test_import_rejects_unsupported_extension(client):
    response = client.post(
        "/import",
        files={"file": ("events.txt", "some data", "text/plain")},
    )

    assert response.status_code == 400
    assert "supported" in response.json()["detail"].lower()
