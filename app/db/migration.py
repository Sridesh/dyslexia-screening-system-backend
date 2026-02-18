import sqlite3
import logging

# Configure basic logging for the migration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_db():
    """
    Checks for missing columns in all tables and adds them if necessary.
    This is a manual migration function to sync the DB schema with models.
    """
    DB_FILE = "./sql_app.db"
    
    try:
        logger.info(f"Checking database schema at {DB_FILE}...")
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Schema mapping based on models: Table -> { Column: Type }
        schema_definitions = {
            "item": {
                "module": "VARCHAR NOT NULL",
                "difficulty": "FLOAT NOT NULL",
                "max_time_s": "FLOAT",
                "prompt_type": "VARCHAR",
                "prompt_text": "TEXT",
                "prompt_media": "VARCHAR",
                "correct_option": "VARCHAR",
                "options_json": "TEXT",
                "is_active": "BOOLEAN DEFAULT 1",
                "created_at": "DATETIME",
                "updated_at": "DATETIME"
            },
            "child": {
                "external_id": "VARCHAR",
                "name": "VARCHAR",
                "dob": "DATETIME",
                "gender": "VARCHAR",
                "language": "VARCHAR",
                "notes": "TEXT",
                "created_at": "DATETIME",
                "updated_at": "DATETIME"
            },
            "test": {
                "child_id": "INTEGER",
                "start_time": "DATETIME",
                "end_time": "DATETIME",
                "final_risk_label": "VARCHAR",
                "final_risk_score": "FLOAT",
                "final_risk_entropy": "FLOAT",
                "total_items": "INTEGER",
                "total_time_s": "FLOAT",
                "final_fatigue_level": "FLOAT",
                "device_id": "VARCHAR",
                "version": "VARCHAR",
                "notes": "TEXT",
                "session_state": "TEXT", # JSON
                "status": "VARCHAR DEFAULT 'in_progress'",
                "created_at": "DATETIME",
                "updated_at": "DATETIME"
            },
            "test_item_log": {
                "test_id": "INTEGER",
                "item_id": "INTEGER",
                "round_number": "INTEGER",
                "within_round_idx": "INTEGER",
                "global_index": "INTEGER",
                "module": "VARCHAR",
                "difficulty": "FLOAT",
                "response": "TEXT",
                "is_correct": "BOOLEAN",
                "response_time_s": "FLOAT",
                "started_at": "DATETIME",
                "submitted_at": "DATETIME",
                "is_switch_question": "BOOLEAN DEFAULT 0",
                "was_slow_correct": "BOOLEAN DEFAULT 0",
                "fatigue_factor_used": "FLOAT",
                "p_module_weak_before": "FLOAT",
                "p_module_strong_before": "FLOAT",
                "p_module_weak_after": "FLOAT",
                "p_module_strong_after": "FLOAT",
                "p_risk_atrisk_before": "FLOAT",
                "p_risk_atrisk_after": "FLOAT",
                "created_at": "DATETIME"
            },
            "test_features": {
                "test_id": "INTEGER",
                "p_risk_atrisk": "FLOAT",
                "risk_entropy": "FLOAT",
                "total_items": "INTEGER",
                "total_time_s": "FLOAT",
                "final_fatigue": "FLOAT",
                "p_weak_RAN": "FLOAT",
                "entropy_RAN": "FLOAT",
                "num_items_RAN": "INTEGER",
                "avg_time_RAN": "FLOAT",
                "slow_corr_ratio_RAN": "FLOAT",
                "avg_switch_rt_RAN": "FLOAT",
                "p_weak_phonology": "FLOAT",
                "entropy_phonology": "FLOAT",
                "num_items_phonology": "INTEGER",
                "avg_time_phonology": "FLOAT",
                "slow_corr_ratio_phonology": "FLOAT",
                "avg_switch_rt_phonology": "FLOAT",
                "created_at": "DATETIME"
            },
            "test_module_sum": {
                "test_id": "INTEGER",
                "module": "VARCHAR",
                "risk_label": "VARCHAR",
                "p_weak_final": "FLOAT",
                "p_strong_final": "FLOAT",
                "entropy_final": "FLOAT",
                "num_items": "INTEGER",
                "avg_time_s": "FLOAT",
                "min_time_s": "FLOAT",
                "max_time_s": "FLOAT",
                "slow_correct_count": "INTEGER",
                "total_correct_count": "INTEGER",
                "slow_correct_ratio": "FLOAT",
                "avg_switch_rt_s": "FLOAT",
                "switch_count": "INTEGER",
                "first_round_seen": "INTEGER",
                "last_round_seen": "INTEGER",
                "created_at": "DATETIME"
            },
            "test_xai": {
                "test_id": "INTEGER",
                "method": "VARCHAR",
                "payload_json": "TEXT",
                "created_at": "DATETIME"
            }
        }

        changes_made = False
        for table, expected_columns in schema_definitions.items():
            # Check if table exists
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
            if not cursor.fetchone():
                logger.info(f"Table '{table}' does not exist yet. It will be created by SQLAlchemy.")
                continue

            # Get existing columns
            cursor.execute(f"PRAGMA table_info({table})")
            existing_cols = {row[1] for row in cursor.fetchall()}
            
            for col, col_type in expected_columns.items():
                if col not in existing_cols:
                    logger.warning(f"Column '{col}' is missing in '{table}' table. Adding it...")
                    try:
                        cursor.execute(f"ALTER TABLE {table} ADD COLUMN {col} {col_type}")
                        changes_made = True
                        logger.info(f"Successfully added column '{col}' to '{table}'.")
                    except Exception as e:
                        logger.error(f"Failed to add column '{col}' to '{table}': {e}")
        
        if changes_made:
            conn.commit()
            logger.info("Database migration committed.")
        else:
            logger.info("Database schema is fully up to date.")
            
        conn.close()
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")

if __name__ == "__main__":
    migrate_db()
