from __future__ import annotations


def seed_events(client, sample_csv):
    response = client.post(
        "/import",
        files={"file": ("events.csv", sample_csv, "text/csv")},
    )
    assert response.status_code == 200


def test_filters_by_level(client, sample_csv):
    seed_events(client, sample_csv)

    response = client.get("/events", params={"level": "ERROR"})

    assert response.status_code == 200
    rows = response.json()
    assert len(rows) == 1
    assert rows[0]["level"] == "ERROR"


def test_filters_by_source_and_query(client, sample_csv):
    seed_events(client, sample_csv)

    response = client.get(
        "/events",
        params={"source": "sensor-temp-01", "q": "drift"},
    )

    assert response.status_code == 200
    rows = response.json()
    assert len(rows) == 1
    assert rows[0]["source"] == "sensor-temp-01"
    assert "drift" in rows[0]["message"]


def test_filters_by_date_range(client, sample_csv):
    seed_events(client, sample_csv)

    response = client.get(
        "/events",
        params={
            "start": "2026-02-28T21:09:00+05:00",
            "end": "2026-02-28T21:09:59+05:00",
        },
    )

    assert response.status_code == 200
    rows = response.json()
    assert len(rows) == 1
    assert rows[0]["level"] == "ERROR"


def test_rejects_invalid_level(client, sample_csv):
    seed_events(client, sample_csv)

    response = client.get("/events", params={"level": "DEBUG"})

    assert response.status_code == 400
    assert "INFO,WARN,ERROR" in response.json()["detail"]
