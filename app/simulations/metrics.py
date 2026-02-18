from typing import Dict, Any, List

def compute_metrics(results: Dict[str, Dict]) -> Dict[str, float]:
    TP = 0
    FP = 0
    TN = 0
    FN = 0
    
    items_risk = []
    items_safe = []

    for prof_name, data in results.items():
        gt = data["ground_truth"]
        
        for r in data["runs"]:
            cat = r["risk_category"]
            # Definition: High/Moderate is "Positive" (Risk) result
            predicted_positive = cat in ("high", "moderate")
            
            if gt == "at_risk":
                if predicted_positive:
                    TP += 1
                else:
                    FN += 1
                items_risk.append(r["total_items"])
            else:
                # ground_truth == "not_at_risk"
                if predicted_positive:
                    FP += 1
                else:
                    TN += 1
                items_safe.append(r["total_items"])

    sens = TP / (TP + FN) if (TP + FN) > 0 else 0.0
    spec = TN / (TN + FP) if (TN + FP) > 0 else 0.0
    j = sens + spec - 1  # Youden index

    avg_risk = sum(items_risk) / len(items_risk) if items_risk else 0.0
    avg_safe = sum(items_safe) / len(items_safe) if items_safe else 0.0
    avg_all = (sum(items_risk) + sum(items_safe)) / max(len(items_risk) + len(items_safe), 1)

    return {
        "sensitivity": sens,
        "specificity": spec,
        "youden_j": j,
        "avg_items_atrisk": avg_risk,
        "avg_items_notrisk": avg_safe,
        "avg_items_all": avg_all,
        "TP": TP, "FP": FP, "TN": TN, "FN": FN,
    }
