import sys
import os
import json
from datetime import datetime
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.append(os.getcwd())

from app.main import app
from app.db.database import Base, get_db
from app.api.deps import deps
from app import models

# Setup in-memory DB for testing with JSON support (SQLite modern usually ok)
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_refactor.db"
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
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

client = TestClient(app)

def test_refactored_flow():
    print("Starting refactored flow test...")
    db = TestingSessionLocal()
    
    # 1. Reset & Seed Items
    db.query(models.item.Item).delete()
    modules = ["phonemic_awareness", "ran", "object_recognition"]
    for mod in modules:
        for i in range(5):
            item = models.item.Item(
                module=mod,
                difficulty=0.5 + (i * 0.1),
                max_time_s=60.0,
                prompt_text=f"Prompt {i}",
                correct_option="A",
                options_json='["A", "B", "C"]',
                is_active=True,
                created_at=datetime.utcnow()
            )
            db.add(item)
    db.commit()

    # 2. Child perms
    resp = client.post("/api/v1/children/", json={"name": "Refactor Child", "external_id": "REF001"})
    child_id = resp.json()["id"]

    # 3. Start Test
    # Using /start
    print("Testing /adaptive/start...")
    start_payload = {"child_id": child_id, "device_id": "DEVICE_REF"}
    resp = client.post("/api/v1/adaptive/start", json=start_payload)
    if resp.status_code != 200:
        print(f"Start failed: {resp.text}")
        sys.exit(1)
    
    start_data = resp.json()
    test_id = start_data["test_id"]
    next_item = start_data.get("first_item")
    assert next_item is not None
    # Check new content fields
    assert "options_json" in next_item
    print(f"First item: {next_item['id']} Options: {next_item['options_json']}")

    # 4. Submit Response
    # Using /responses
    print("Testing /responses...")
    log_data = {
        "test_id": test_id,
        "item_id": next_item["id"],
        "module": next_item["module_id"],
        "response": "A",
        "is_correct": True,
        "response_time_s": 2.0,
        "started_at": datetime.utcnow().isoformat(),
        "submitted_at": datetime.utcnow().isoformat()
    }
    resp = client.post(f"/api/v1/adaptive/{test_id}/responses", json=log_data)
    if resp.status_code != 200:
        print(f"Response failed: {resp.text}")
        sys.exit(1)
    
    resp_data = resp.json()
    print(f"Response status: {resp_data['status']}")
    if resp_data['status'] == 'in_progress':
        assert "next_item" in resp_data
    
    print("Refactor verified successfully!")

if __name__ == "__main__":
    try:
        test_refactored_flow()
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
