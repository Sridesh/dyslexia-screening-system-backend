from dataclasses import dataclass
from typing import Dict, List, Literal

@dataclass
class SyntheticChild:
    name: str
    theta_by_module: Dict[str, float]
    ground_truth: Literal["at_risk", "not_at_risk"]

PROFILES: List[SyntheticChild] = [
    SyntheticChild(
        name="Strong_All",
        theta_by_module={
            "phonemic_awareness": 1.5,
            "ran": 1.5,
            "object_recognition": 1.0,
        },
        ground_truth="not_at_risk",
    ),
    SyntheticChild(
        name="Average_Kid",
        theta_by_module={
            "phonemic_awareness": 0.0,
            "ran": 0.0,
            "object_recognition": 0.0,
        },
        ground_truth="not_at_risk",
    ),
    SyntheticChild(
        name="Weak_PA_RAN",
        theta_by_module={
            "phonemic_awareness": -1.5,
            "ran": -1.5,
            "object_recognition": 0.0,
        },
        ground_truth="at_risk",
    ),
    SyntheticChild(
        name="Weak_RAN_Only",
        theta_by_module={
            "phonemic_awareness": 0.5,
            "ran": -1.5,
            "object_recognition": 0.0,
        },
        ground_truth="at_risk",  # Depends on definition, usually significant
    ),
]
