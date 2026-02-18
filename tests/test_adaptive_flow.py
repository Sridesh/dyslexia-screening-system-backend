import sys
import os
import json
from datetime import datetime
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add current directory to sys.path
sys.path.append(os.getcwd())

from app.main import app
from app.db.database import Base, get_db
from app.api.deps import deps
from app import models

# Setup in-memory DB for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_adaptive.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[deps.get_db] = override_get_db

# Create tables
Base.metadata.create_all(bind=engine)

client = TestClient(app)

def test_adaptive_flow():
    print("Starting adaptive flow test...")
    db = TestingSessionLocal()
    
    # 1. Create dummy items if not exist
    # (In a real scenario we'd fixture this, but here we just ensure DB has items)
    # Check if items exist
    if db.query(models.item.Item).count() == 0:
        print("Seeding dummy items...")
        modules = ["phonemic_awareness", "ran", "object_recognition"]
        for mod in modules:
            for i in range(5):
                item = models.item.Item(
                    module=mod,
                    difficulty=0.5 + (i * 0.1),
                    max_time_s=60.0,
                    prompt_text=f"Item {i} for {mod}",
                    is_active=True,
                    created_at=datetime.utcnow()
                )
                db.add(item)
        db.commit()

    # 2. Create a Child
    print("Creating child...")
    resp = client.post("/api/v1/children/", json={"name": "Test Child", "external_id": "TEST001"})
    assert resp.status_code == 201
    child_id = resp.json()["id"]
    print(f"Child created: {child_id}")

    # 3. Create a Test
    print("Creating test...")
    resp = client.post("/api/v1/tests/", json={"child_id": child_id, "device_id": "TEST_DEVICE"})
    assert resp.status_code == 201
    test_id = resp.json()["id"]
    print(f"Test created: {test_id}")

    # 4. Start Adaptive Test
    print("Starting adaptive test...")
    resp = client.post(f"/api/v1/adaptive/{test_id}/start")
    if resp.status_code != 200:
        print(f"Start failed: {resp.text}")
        sys.exit(1)
    
    start_data = resp.json()
    assert "next_item" in start_data
    first_item = start_data["next_item"]
    print(f"First item received: {first_item['id']} ({first_item['module']})")

    # 5. Submit Response
    print("Submitting response...")
    log_data = {
        "test_id": test_id,
        "item_id": first_item["id"],
        "module": first_item["module"],
        "response": "correct",
        "is_correct": True,
        "response_time_s": 2.5,
        "started_at": datetime.utcnow().isoformat(),
        "submitted_at": datetime.utcnow().isoformat()
    }
    resp = client.post(f"/api/v1/adaptive/{test_id}/submit", json=log_data)
    if resp.status_code != 200:
        print(f"Submit failed: {resp.text}")
        sys.exit(1)
    
    submit_data = resp.json()
    if submit_data.get("complete"):
        print("Test complete (unexpectedly early but possible if logic triggers).")
        print("Results:", submit_data["results"])
    else:
        next_item = submit_data["next_item"]
        print(f"Next item received: {next_item['id']} ({next_item['module']})")
        assert next_item["id"] != first_item["id"]

    print("Adaptive flow verified successfully!")

if __name__ == "__main__":
    try:
        test_adaptive_flow()
        # Clean up test db file
        # os.remove("./test_adaptive.db") 
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
