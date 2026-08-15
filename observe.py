from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app, catalog_is_loaded


print(f"before TestClient: catalog loaded = {catalog_is_loaded()}")
with TestClient(app) as client:
    print(f"inside TestClient: catalog loaded = {catalog_is_loaded()}")
    response = client.get("/health")
    print(f"response status: {response.status_code}")
    print(f"response body: {response.json()}")
print(f"after TestClient: catalog loaded = {catalog_is_loaded()}")
