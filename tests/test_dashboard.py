from __future__ import annotations


def seed_for_dashboard(client, sample_csv):
    response = client.post(
        "/import",
        files={"file": ("events.csv", sample_csv, "text/csv")},
    )
    assert response.status_code == 200


def test_dashboard_metrics_are_consistent(client, sample_csv):
    seed_for_dashboard(client, sample_csv)

    response = client.get("/dashboard")

    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 3
    assert payload["by_level"]["INFO"] == 1
    assert payload["by_level"]["WARN"] == 1
    assert payload["by_level"]["ERROR"] == 1
    assert payload["unique_sources"] == 2
    assert len(payload["latest"]) == 3


def test_dashboard_top_sources_for_error_and_warn(client):
    csv_content = (
        "timestamp,source,level,message,metric_value,tag\n"
        "2026-02-28T21:01:00+05:00,logger-1,ERROR,Error 1,,io\n"
        "2026-02-28T21:02:00+05:00,logger-1,ERROR,Error 2,,io\n"
        "2026-02-28T21:03:00+05:00,logger-2,ERROR,Error 3,,io\n"
        "2026-02-28T21:04:00+05:00,sensor-a,WARN,Warn 1,1.0,temp\n"
        "2026-02-28T21:05:00+05:00,sensor-a,WARN,Warn 2,1.1,temp\n"
        "2026-02-28T21:06:00+05:00,sensor-b,WARN,Warn 3,1.2,temp\n"
    )
    import_response = client.post(
        "/import",
        files={"file": ("events.csv", csv_content, "text/csv")},
    )
    assert import_response.status_code == 200

    response = client.get("/dashboard/top-sources", params={"limit": 2})

    assert response.status_code == 200
    payload = response.json()

    assert payload["ERROR"][0] == {"source": "logger-1", "count": 2}
    assert payload["ERROR"][1] == {"source": "logger-2", "count": 1}
    assert payload["WARN"][0] == {"source": "sensor-a", "count": 2}
    assert payload["WARN"][1] == {"source": "sensor-b", "count": 1}
