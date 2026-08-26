import os

os.environ["DATABASE_URL"] = "sqlite://"
os.environ["SECRET_KEY"] = "test-secret"

from fastapi.testclient import TestClient

from app.main import app
from app.db.base import Base
from app.db.seed import seed_analytics_setup, seed_sales_dataset, seed_usuarios
from app.db.session import SessionLocal, engine
from app.services.chatbot_service import is_safe_select

Base.metadata.create_all(bind=engine)
db = SessionLocal()
try:
    seed_usuarios(db)
    seed_sales_dataset(db)
    seed_analytics_setup(db)
finally:
    db.close()

client = TestClient(app)


def auth_headers():
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "analyst@brainwave.bi", "password": "analyst123"},
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_health_check():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "running"


def test_sql_safety_blocks_writes():
    assert is_safe_select("SELECT product FROM salerecord")
    assert not is_safe_select("DELETE FROM salerecord")
    assert not is_safe_select("SELECT * FROM salerecord; DROP TABLE usuario")


def test_chat_analysis_returns_table_chart_and_sql():
    response = client.post(
        "/api/v1/chat/ask",
        json={"question": "Qual produto vendeu mais?"},
        headers=auth_headers(),
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["sql"].lower().startswith("select")
    assert payload["rows"]
    assert payload["chart"]["labels"]
    assert payload["insights"]


def test_dataset_sample_has_seeded_sales():
    response = client.get("/api/v1/datasets/sales/sample", headers=auth_headers())
    assert response.status_code == 200
    assert len(response.json()) > 0


def test_analytics_overview_returns_business_metrics():
    response = client.get("/api/v1/analytics/overview", headers=auth_headers())
    assert response.status_code == 200
    payload = response.json()
    assert payload["metrics"]
    assert payload["monthly_revenue"]
    assert payload["top_products"]


def test_alerts_are_available_and_refresh_values():
    response = client.get("/api/v1/alerts", headers=auth_headers())
    assert response.status_code == 200
    alerts = response.json()
    assert alerts
    assert "current_value" in alerts[0]


def test_report_generation_and_listing():
    create_response = client.post(
        "/api/v1/reports",
        json={"title": "Resumo executivo", "period": "2026-H1"},
        headers=auth_headers(),
    )
    assert create_response.status_code == 200
    report = create_response.json()
    assert report["summary"]
    assert report["payload"]["metrics"]

    list_response = client.get("/api/v1/reports", headers=auth_headers())
    assert list_response.status_code == 200
    assert len(list_response.json()) >= 1
