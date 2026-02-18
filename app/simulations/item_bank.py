import csv
from typing import Dict, List, Tuple
from app.adaptive_testing_module.selection import CandidateItem

def load_item_bank_from_csv(path: str = "ef_ads_item_bank.csv") -> Tuple[Dict[int, CandidateItem], Dict[str, List[int]]]:
    items: Dict[int, CandidateItem] = {}
    module_item_ids: Dict[str, List[int]] = {}
    
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            item_id = int(row["id"])
            module = row["module"]
            difficulty = float(row["difficulty"])
            max_time_s = float(row["max_time_s"])
            
            items[item_id] = CandidateItem(
                id=item_id,
                module_id=module,
                difficulty=difficulty,
                max_time_seconds=max_time_s,
            )
            module_item_ids.setdefault(module, []).append(item_id)
            
    return items, module_item_ids
