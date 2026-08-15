from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app, catalog_is_loaded


print(f"before TestClient: catalog loaded = {catalog_is_loaded()}")
client = TestClient(app)
response = client.get("/health")
print(f"response status: {response.status_code}")
print(f"response body: {response.json()}")
print(f"after request: catalog loaded = {catalog_is_loaded()}")
client.close()
