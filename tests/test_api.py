"""
API endpoint tests.
"""

from fastapi.testclient import TestClient

from app import app

client = TestClient(
    app,
    raise_server_exceptions=False,
)


def test_root_endpoint() -> None:
    """
    Verify the root endpoint.
    """

    response = client.get("/api/v1/")

    assert response.status_code == 200

    data = response.json()

    assert data == {
        "application": "Autonomous AI Agent",
        "version": "1.0.0",
        "status": "running",
    }


def test_health_endpoint() -> None:
    """
    Verify the health endpoint.
    """

    response = client.get("/api/v1/health")

    assert response.status_code == 200

    assert response.json() == {
        "status": "healthy",
    }


def test_error_endpoint() -> None:
    """
    Verify global exception handling.
    """

    response = client.get("/api/v1/error")

    assert response.status_code == 500

    body = response.json()

    assert "error" in body
    assert "detail" in body
    assert "request_id" in body