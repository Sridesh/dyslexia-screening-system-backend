from sqlalchemy.orm import Session
from typing import Dict, Any
import json

from app.models.test import Test
from app.adaptive_testing_module.state import SessionState # Assuming this import path based on user request, but actual path is app.adaptive_testing_module.state
# Correction: The actual path in previous context was app.adaptive_testing_module.state
# I should use the correct path or check if user renamed it. User said "not in ef_ads" for service, but import might process.
# I will use app.adaptive_testing_module.state as per my previous file views.

from app.adaptive_testing_module.state import SessionState

def save_session_snapshot(db: Session, test: Test, session_state: SessionState) -> None:
    """
    Serialise SessionState to dict and store it in Test.session_state.
    """
    snapshot: Dict = session_state.to_snapshot()
    # SQLAlchemy with JSON type handles dict -> json serialization
    test.session_state = snapshot
    db.add(test)

def load_session_state(test: Test) -> SessionState:
    """
    Reconstruct SessionState from Test.session_state.

    Raises ValueError if snapshot is missing.
    """
    if not test.session_state:
        raise ValueError("Test has no session_state stored")

    if isinstance(test.session_state, str):
         # Handle legacy or SQLite Text case if migration didn't convert data
         snapshot_dict = json.loads(test.session_state)
    else:
         snapshot_dict = test.session_state
         
    return SessionState.from_snapshot(snapshot_dict)
