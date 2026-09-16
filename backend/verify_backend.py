import sys
from fastapi.testclient import TestClient
from main import app
from app.services.simulation import calculate_simulation

client = TestClient(app)

def test_all():
    print("Testing FastAPI endpoints...")
    
    r = client.get("/")
    assert r.status_code == 200, f"Root status: {r.status_code}"
    print("[PASS] GET / -> 200 OK")
    
    r = client.get("/api/dashboard/summary")
    assert r.status_code == 200, f"Dashboard summary: {r.status_code}"
    data = r.json()
    assert "health_score" in data
    assert "peer_benchmark" in data
    print(f"[PASS] GET /api/dashboard/summary -> 200 OK (Score: {data['health_score']}, Benchmark: {data['peer_benchmark']['percentile']}th percentile)")
    
    r = client.get("/api/machines")
    assert r.status_code == 200
    machines = r.json()
    assert len(machines) >= 5
    print(f"[PASS] GET /api/machines -> 200 OK ({len(machines)} machines)")
    
    r = client.get("/api/machines/induction-furnace-01")
    assert r.status_code == 200
    m_detail = r.json()
    assert m_detail["name"] == "Induction Furnace 01"
    print(f"[PASS] GET /api/machines/induction-furnace-01 -> 200 OK ({m_detail['reading']})")
    
    r = client.get("/api/alerts")
    assert r.status_code == 200
    alerts = r.json()
    assert len(alerts) >= 4
    print(f"[PASS] GET /api/alerts -> 200 OK ({len(alerts)} alerts)")
    
    r = client.get("/api/recommendations")
    assert r.status_code == 200
    recs = r.json()
    assert len(recs) >= 4
    print(f"[PASS] GET /api/recommendations -> 200 OK ({len(recs)} recommendations)")
    
    r = client.get("/api/schemes?industry_type=foundry")
    assert r.status_code == 200
    schemes = r.json()
    assert len(schemes) >= 3
    print(f"[PASS] GET /api/schemes -> 200 OK ({len(schemes)} schemes)")
    
    r = client.post("/api/simulate", json={"intervention_type": "load_shift", "params": {"shift_kwh_per_day": 500}})
    assert r.status_code == 200
    sim = r.json()
    assert sim["projected_savings_rupees_per_month"] > 0
    print(f"[PASS] POST /api/simulate -> 200 OK (Savings: Rs.{sim['projected_savings_rupees_per_month']}/mo, Payback: {sim['payback_months']} mo)")
    
    print("\nAll Backend API tests passed successfully!")

if __name__ == "__main__":
    test_all()
