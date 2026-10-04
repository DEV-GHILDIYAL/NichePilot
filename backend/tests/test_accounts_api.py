import uuid
from datetime import UTC, datetime

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.exc import DBAPIError


def create(client, auth, payload):
    response = client.post("/api/v1/accounts", json=payload, headers=auth)
    assert response.status_code == 201, response.text
    return response.json()


def test_authorization_and_account_lifecycle(client, auth, account_payload):
    assert client.get("/health/live").status_code == 200
    assert client.get("/health/ready").status_code == 200
    assert client.get("/api/v1/accounts").status_code == 401
    assert (
        client.get("/api/v1/accounts", headers={"Authorization": "Bearer wrong"}).status_code == 403
    )

    account = create(client, auth, account_payload)
    account_id = account["id"]
    assert account["paused"] is True
    assert account["version"] == 1
    assert client.get("/api/v1/accounts", headers=auth).json()[0]["id"] == account_id
    assert client.get(f"/api/v1/accounts/{account_id}", headers=auth).json()["id"] == account_id
    assert client.get(f"/api/v1/accounts/{uuid.uuid4()}", headers=auth).status_code == 404

    duplicate = client.post("/api/v1/accounts", json=account_payload, headers=auth)
    assert duplicate.status_code == 409
    updated = client.patch(
        f"/api/v1/accounts/{account_id}",
        json={"display_name": "Workday Comedy", "expected_version": 1},
        headers=auth,
    )
    assert updated.status_code == 200
    assert updated.json()["version"] == 2
    assert (
        client.post(f"/api/v1/accounts/{account_id}/resume", headers=auth).json()["paused"] is False
    )
    assert (
        client.post(f"/api/v1/accounts/{account_id}/pause", headers=auth).json()["paused"] is True
    )
    events = client.get(f"/api/v1/accounts/{account_id}/events", headers=auth).json()["items"]
    assert [item["action"] for item in events] == [
        "account_paused",
        "account_resumed",
        "account_updated",
        "account_created",
    ]
    assert all(item["account_id"] == account_id for item in events)


def test_revisions_are_immutable_and_stale_update_conflicts(
    client, auth, account_payload, database_url
):
    account = create(client, auth, account_payload)
    account_id = account["id"]
    path = f"/api/v1/accounts/{account_id}/niche-dna"
    first = client.get(path, headers=auth).json()
    assert first["revision_number"] == 1
    new_data = account_payload["niche_dna"] | {
        "niche_name": "Indian office comedy",
        "change_note": "Narrowed focus",
        "expected_active_revision_number": 1,
    }
    revised = client.post(f"{path}/revisions", json=new_data, headers=auth)
    assert revised.status_code == 201, revised.text
    assert revised.json()["revision_number"] == 2
    assert client.post(f"{path}/revisions", json=new_data, headers=auth).status_code == 409
    history = client.get(f"{path}/revisions", headers=auth).json()
    assert [item["revision_number"] for item in history] == [2, 1]
    assert history[1]["niche_name"] == first["niche_name"]
    events = client.get(f"/api/v1/accounts/{account_id}/events", headers=auth).json()["items"]
    assert [item["action"] for item in events] == ["niche_dna_revised", "account_created"]
    assert events[0]["old_revision_id"] == first["id"]
    assert events[0]["new_revision_id"] == revised.json()["id"]

    engine = create_engine(database_url)
    with engine.connect() as connection:
        with pytest.raises(DBAPIError):
            connection.execute(
                text("UPDATE niche_dna_revisions SET niche_name='changed' WHERE id=:id"),
                {"id": uuid.UUID(first["id"])},
            )
        connection.rollback()
    engine.dispose()
    assert client.get(path, headers=auth).json()["niche_name"] == "Indian office comedy"


def test_account_isolation_and_event_pagination(client, auth, account_payload, database_url):
    first = create(client, auth, account_payload)
    second_payload = account_payload | {
        "display_name": "College Comedy",
        "platform_handle": "college.comedy",
    }
    second = create(client, auth, second_payload)
    first_id, second_id = first["id"], second["id"]
    client.post(f"/api/v1/accounts/{first_id}/resume", headers=auth)
    client.post(f"/api/v1/accounts/{first_id}/pause", headers=auth)
    assert (
        len(client.get(f"/api/v1/accounts/{second_id}/events", headers=auth).json()["items"]) == 1
    )
    assert (
        client.get(f"/api/v1/accounts/{second_id}/niche-dna", headers=auth).json()["account_id"]
        == second_id
    )

    with create_engine(database_url).connect() as connection:
        with pytest.raises(DBAPIError):
            connection.execute(
                text(
                    "UPDATE accounts SET active_niche_revision_id=:foreign_revision "
                    "WHERE id=:account_id"
                ),
                {
                    "foreign_revision": uuid.UUID(second["active_niche_revision_id"]),
                    "account_id": uuid.UUID(first_id),
                },
            )
        connection.rollback()

    engine = create_engine(database_url)
    with engine.begin() as connection:
        timestamp = datetime(2026, 1, 1, tzinfo=UTC)
        connection.execute(
            text(
                "UPDATE account_change_events SET occurred_at=:timestamp "
                "WHERE account_id=:account_id"
            ),
            {"timestamp": timestamp, "account_id": uuid.UUID(first_id)},
        )
    engine.dispose()
    seen = []
    cursor = None
    while True:
        params = {"limit": 1}
        if cursor:
            params["cursor"] = cursor
        page = client.get(f"/api/v1/accounts/{first_id}/events", params=params, headers=auth).json()
        seen.extend(item["id"] for item in page["items"])
        cursor = page["next_cursor"]
        if not cursor:
            break
    assert len(seen) == 3
    assert len(set(seen)) == 3
    assert (
        client.get(
            f"/api/v1/accounts/{first_id}/events", params={"limit": 101}, headers=auth
        ).status_code
        == 422
    )
    assert (
        client.get(
            f"/api/v1/accounts/{first_id}/events", params={"cursor": "invalid"}, headers=auth
        ).status_code
        == 422
    )


def test_invalid_requests_leave_no_events(client, auth, account_payload):
    account = create(client, auth, account_payload)
    account_id = account["id"]
    path = f"/api/v1/accounts/{account_id}"
    assert (
        client.patch(
            path, json={"display_name": " ", "expected_version": 1}, headers=auth
        ).status_code
        == 422
    )
    assert (
        client.patch(path, json={"paused": False, "expected_version": 1}, headers=auth).status_code
        == 422
    )
    assert (
        client.patch(
            path, json={"display_name": "Changed", "expected_version": 99}, headers=auth
        ).status_code
        == 409
    )
    assert (
        client.post(
            f"{path}/niche-dna/revisions",
            json=account_payload["niche_dna"] | {"expected_active_revision_number": 99},
            headers=auth,
        ).status_code
        == 409
    )
    events = client.get(f"{path}/events", headers=auth).json()["items"]
    assert len(events) == 1
    assert client.post(f"{path}/pause", headers=auth).status_code == 200
    assert len(client.get(f"{path}/events", headers=auth).json()["items"]) == 1
