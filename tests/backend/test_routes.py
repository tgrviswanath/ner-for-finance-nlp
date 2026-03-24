import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

MOCK_RESULT = {
    "entities": [{"text": "Apple Inc.", "label": "ORG", "label_name": "Organization",
                  "color": "#1976d2", "icon": "🏢", "start": 0, "end": 10}],
    "by_label": {"ORG": ["Apple Inc."]},
    "label_counts": [{"label": "ORG", "label_name": "Organization", "count": 1, "color": "#1976d2"}],
    "total": 1,
    "word_count": 5,
}


@patch("app.core.service.extract", new_callable=AsyncMock)
def test_extract_endpoint(mock_fn):
    mock_fn.return_value = MOCK_RESULT
    response = client.post("/api/v1/extract", json={"text": "Apple Inc. reported strong earnings."})
    assert response.status_code == 200
    assert response.json()["total"] == 1


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
