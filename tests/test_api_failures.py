from fastapi.testclient import TestClient

from app import app

client = TestClient(
    app,
    raise_server_exceptions=False,
)


def test_agent_missing_request_field():
    """
    Request body missing the required 'request' field.
    """

    response = client.post(
        "/api/v1/agent",
        json={},
    )

    assert response.status_code == 422

    body = response.json()

    assert "detail" in body


def test_agent_empty_request():
    """
    Empty request string should fail validation.
    """

    response = client.post(
        "/api/v1/agent",
        json={
            "request": ""
        },
    )

    assert response.status_code == 422


def test_agent_whitespace_request():
    """
    Whitespace-only request should fail validation.
    """

    response = client.post(
        "/api/v1/agent",
        json={
            "request": "     "
        },
    )

    assert response.status_code == 422


def test_agent_invalid_json():
    """
    Invalid JSON body.
    """

    response = client.post(
        "/api/v1/agent",
        content="{invalid json}",
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 422


def test_unknown_route():
    """
    Unknown endpoint should return 404.
    """

    response = client.get(
        "/api/v1/does-not-exist",
    )

    assert response.status_code == 404


def test_invalid_http_method():
    """
    Unsupported HTTP method.
    """

    response = client.put(
        "/api/v1/health",
    )

    assert response.status_code == 405