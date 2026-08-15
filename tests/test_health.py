from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app, catalog_is_loaded


def test_health_endpoint_uses_initialized_catalog() -> None:
    """ヘルスチェックは、起動済みアプリの共有カタログを利用できる。"""
    assert catalog_is_loaded() is False

    client = TestClient(app)
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ready",
        "catalog_release": "2026.08",
    }


def test_catalog_is_not_initialized_before_app_start() -> None:
    """対照ケース: テスト開始時点ではlifespanは未実行である。"""
    assert catalog_is_loaded() is False
