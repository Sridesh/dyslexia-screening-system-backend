from typing import Dict, List
from sqlalchemy.orm import Session
from app.models.item import Item
from app.adaptive_testing_module import selection

def load_active_items(db: Session) -> List[Item]:
    """
    Load all active items from the database.
    """
    return db.query(Item).filter(Item.is_active == True).all()

def build_item_pool(items: List[Item]) -> Dict[int, selection.CandidateItem]:
    """
    Map SQLAlchemy Item objects to EF-ADS CandidateItem objects.

    Returns
    -------
    item_pool: dict mapping item_id -> CandidateItem
    """
    pool: Dict[int, selection.CandidateItem] = {}
    for it in items:
        pool[it.id] = selection.CandidateItem(
            id=it.id,
            module_id=it.module, # distinct from user prompt 'module_id' vs 'module'
            difficulty=it.difficulty,
            max_time_seconds=it.max_time_s or 60.0,
        )
    return pool

def build_module_item_ids(items: List[Item]) -> Dict[str, List[int]]:
    """
    Group item ids by module_id for initialisation of SessionState.

    Returns
    -------
    {module_id: [item_id, ...], ...}
    """
    mapping: Dict[str, List[int]] = {}
    for it in items:
        mapping.setdefault(it.module, []).append(it.id)
    return mapping
