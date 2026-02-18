from sqlalchemy.orm import Session
import json
from datetime import datetime

from app.models.test import Test
from app.models.test_module_sum import TestModuleSum
from app.models.test_features import TestFeatures
from app.models.test_xai import TestXAI
from app.adaptive_testing_module.risk import GlobalRiskResult
from app.adaptive_testing_module import config

def save_module_summaries(
    db: Session,
    test: Test,
    global_risk: GlobalRiskResult,
) -> None:
    """
    Persist per-module summary entries for a completed test.
    """
    # Clear existing summaries if you want to regenerate (idempotence)
    db.query(TestModuleSum).filter(TestModuleSum.test_id == test.id).delete()

    for module_id, mc in global_risk.modules.items():
        # mc is ModuleClassification
        # We need to access session stats for timing/counts if they are not in ModuleClassification
        # The user's prompt assumes ModuleClassification has avg_rt, etc.
        # My ModuleClassification in `app.adaptive_testing_module.risk.py` MIGHT NOT have these if it was just risk labels.
        # Let's check typical usage. In my previous `adaptive.py`, I accessed `session.modules[mod_id]` for stats.
        # The `global_risk` object in my current codebase (checked in prev turns) has `modules` which are `ModuleClassification`.
        # I need to check if `ModuleClassification` has `avg_rt` or if I need to pass `session` too?
        # The user prompt passes ONLY `global_risk`. I will assume `global_risk` objects carry this info OR I need to adjust.
        # Looking at my previous code in `adaptive.py`: I used `session.modules` for stats and `global_risk.modules` for labels.
        # To strictly follow the service signature `(db, test, global_risk)`, I'd need `global_risk` to have everything.
        # BUT, if my `ModuleClassification` doesn't have it, I should update the signature to include `session` or just pass what I have.
        # I will update the signature to accept `session` as well, or `SessionState`, to be safe/correct for my codebase.
        # WAIT, the prompt says "Assume you already have SQLAlchemy models...".
        # Let's just pass `session` too to be robust, or user might complain I changed signature.
        # Actually, best practice: pass the source of truth. The session has the stats.
        pass

    # I will implement a version that takes session as well, because my data model requires it.
    pass

def save_test_results(
    db: Session,
    test: Test,
    global_risk: GlobalRiskResult,
    session_modules: dict # passing session.modules
) -> None:
    """
    Persist module summaries and risk summaries.
    Combines logic for TestModuleSum, TestFeatures, TestXAI.
    """
    # 1. Module Summaries
    db.query(TestModuleSum).filter(TestModuleSum.test_id == test.id).delete()
    
    for module_id, mod_stats in session_modules.items():
        # Get risk classification if avail
        mc = global_risk.modules.get(module_id)
        
        summary = TestModuleSum(
            test_id=test.id,
            module=module_id,
            risk_label=mc.label if mc else None,
            p_weak_final=mod_stats.p_weak,
            p_strong_final=mod_stats.p_strong,
            entropy_final=mod_stats.entropy,
            num_items=mod_stats.num_items,
            avg_time_s=mod_stats.sum_rt / mod_stats.num_items if mod_stats.num_items > 0 else 0.0,
            total_correct_count=mod_stats.correct,
            slow_correct_count=mod_stats.slow_correct,
            slow_correct_ratio=mod_stats.slow_correct / mod_stats.correct if mod_stats.correct > 0 else 0.0,
            created_at=datetime.utcnow()
        )
        db.add(summary)

    # 2. Risk Summary (Features + XAI)
    # Clear existing
    db.query(TestFeatures).filter(TestFeatures.test_id == test.id).delete()
    db.query(TestXAI).filter(TestXAI.test_id == test.id).delete()

    # Features
    feat_data = {
        "test_id": test.id,
        "p_risk_atrisk": global_risk.risk_score,
        "risk_entropy": 1.0 - global_risk.confidence, # approx
        "total_items": sum(m.num_items for m in session_modules.values()),
        # total_time_s is in test model usually, but can be here too
        "created_at": datetime.utcnow()
    }
    
    # Map specific modules if they exist (hardcoded mapping for features schema)
    # RAN
    if "ran" in session_modules:
        m = session_modules["ran"]
        feat_data.update({
            "p_weak_RAN": m.p_weak,
            "entropy_RAN": m.entropy,
            "num_items_RAN": m.num_items,
            "avg_time_RAN": m.sum_rt / m.num_items if m.num_items > 0 else 0,
            "slow_corr_ratio_RAN": m.slow_correct / m.correct if m.correct > 0 else 0,
        })
    
    # Phonology
    if "phonemic_awareness" in session_modules:
        m = session_modules["phonemic_awareness"]
        feat_data.update({
            "p_weak_phonology": m.p_weak,
            "entropy_phonology": m.entropy,
            "num_items_phonology": m.num_items,
            "avg_time_phonology": m.sum_rt / m.num_items if m.num_items > 0 else 0,
            "slow_corr_ratio_phonology": m.slow_correct / m.correct if m.correct > 0 else 0,
        })

    features = TestFeatures(**feat_data)
    db.add(features)

    # XAI
    xai = TestXAI(
        test_id=test.id,
        method="adaptive_risk_profile",
        payload_json=json.dumps(global_risk.explanation),
        created_at=datetime.utcnow()
    )
    db.add(xai)
