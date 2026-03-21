@echo off
echo Resetting database... > scripts\reset_log.txt
python scripts\reset_db_items.py >> scripts\reset_log.txt 2>&1
echo Done. >> scripts\reset_log.txt
