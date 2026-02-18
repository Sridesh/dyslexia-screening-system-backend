import sqlite3
import os
import sys

# Add current directory to path so we can import app
sys.path.append(os.getcwd())

from app.db.migration import migrate_db

def insert_seed_data():
    # 1. Run migration to ensure prompt_type exists
    print("Running migration...")
    migrate_db()
    
    DB_FILE = "sql_app.db"
    if not os.path.exists(DB_FILE):
        print(f"Error: {DB_FILE} not found.")
        return

    print(f"Inserting seed data into {DB_FILE}...")
    
    sql = """
    INSERT INTO item (id, module, difficulty, max_time_s, prompt_type, prompt_text,
                      prompt_media, correct_option, options_json, is_active)
    VALUES
      (1,  'phonemic_awareness', -2.0, 8.0,  'audio_text',   'Do these words rhyme? CAT - HAT',
           NULL, 'yes', '["yes", "no"]', TRUE),
      (2,  'phonemic_awareness', -1.5, 8.0,  'audio_text',   'Do these words rhyme? TREE - BEE',
           NULL, 'yes', '["yes", "no"]', TRUE),
      (3,  'phonemic_awareness', -1.0, 10.0, 'audio_text',   'Which word starts with the same sound as SUN? Pick one: SOCK, BALL, TREE',
           NULL, 'sock', '["sock", "ball", "tree"]', TRUE),
      (4,  'phonemic_awareness', -0.5, 10.0, 'audio_text',   'Put these sounds together to make a word: /d/ /o/ /g/',
           NULL, 'dog', '["dog", "dig", "bag", "dot"]', TRUE),
      (5,  'phonemic_awareness',  0.0, 12.0, 'audio_text',   'Put these sounds together to make a word: /s/ /t/ /o/ /p/',
           NULL, 'stop', '["stop", "step", "top", "spot"]', TRUE),
      (6,  'phonemic_awareness',  0.5, 12.0, 'audio_text',   'How many sounds do you hear in the word FISH?',
           NULL, '3', '["2", "3", "4", "5"]', TRUE),
      (7,  'phonemic_awareness',  1.0, 15.0, 'audio_text',   'Say SPOT. Now say it again without the /s/ sound. What word is left?',
           NULL, 'pot', '["pot", "top", "sot", "pop"]', TRUE),
      (8,  'phonemic_awareness',  1.5, 15.0, 'audio_text',   'Say CLAP. Now say it again without the /l/ sound. What word is left?',
           NULL, 'cap', '["cap", "lap", "tap", "clap"]', TRUE),
      (9,  'ran',                -2.0, 5.0,  'image',        'Name this object as fast as you can',
           'images/ran/sun.png', 'sun', NULL, TRUE),
      (10, 'ran',                -1.5, 5.0,  'image',        'Name this object as fast as you can',
           'images/ran/car.png', 'car', NULL, TRUE),
      (11, 'ran',                -1.0, 5.0,  'image',        'Name this color as fast as you can',
           'images/ran/red_square.png', 'red', NULL, TRUE),
      (12, 'ran',                -0.5, 6.0,  'image',        'Name this object as fast as you can',
           'images/ran/apple.png', 'apple', NULL, TRUE),
      (13, 'ran',                 0.0, 5.0,  'image',        'Name this letter as fast as you can',
           'images/ran/letter_B.png', 'B', NULL, TRUE),
      (14, 'ran',                 0.5, 5.0,  'image',        'Name this number as fast as you can',
           'images/ran/number_7.png', '7', NULL, TRUE),
      (15, 'ran',                 1.0, 6.0,  'image',        'Name this color as fast as you can',
           'images/ran/purple_square.png', 'purple', NULL, TRUE),
      (16, 'ran',                 1.5, 8.0,  'image',        'Name these items left to right as fast as you can: A 3 B 5',
           'images/ran/alternating_A3B5.png', 'A 3 B 5', NULL, TRUE),
      (17, 'object_recognition', -2.0, 8.0,  'image_choice', 'Which picture shows a DOG?',
           'images/obj/dog_cat_bird_fish.png', 'A', '["A", "B", "C", "D"]', TRUE),
      (18, 'object_recognition', -1.5, 8.0,  'image_choice', 'Which shape is DIFFERENT from the others?',
           'images/obj/three_circles_one_square.png', 'D', '["A", "B", "C", "D"]', TRUE),
      (19, 'object_recognition', -1.0, 10.0, 'image_choice', 'Which arrow points to the RIGHT?',
           'images/obj/arrows_directions.png', 'B', '["A", "B", "C", "D"]', TRUE),
      (20, 'object_recognition', -0.5, 10.0, 'image_choice', 'Find the picture that matches the one in the box',
           'images/obj/shape_match_easy.png', 'C', '["A", "B", "C", "D"]', TRUE),
      (21, 'object_recognition',  0.0, 10.0, 'image_choice', 'Which one is the letter b?',
           'images/obj/b_d_p_q.png', 'A', '["A (b)", "B (d)", "C (p)", "D (q)"]', TRUE),
      (22, 'object_recognition',  0.5, 12.0, 'image_choice', 'Which picture is the MIRROR IMAGE of the one in the box?',
           'images/obj/mirror_image_moderate.png', 'B', '["A", "B", "C", "D"]', TRUE),
      (23, 'object_recognition',  1.0, 15.0, 'image_choice', 'Which symbol sequence matches the one shown? Look carefully at the order',
           'images/obj/symbol_sequence_hard.png', 'C', '["A", "B", "C", "D"]', TRUE),
      (24, 'object_recognition',  1.5, 15.0, 'image_choice', 'Find the hidden shape inside the larger pattern',
           'images/obj/embedded_figure.png', 'B', '["A", "B", "C", "D"]', TRUE);
    """
    
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Check if items already exist to avoid duplicates if rerun
        cursor.execute("SELECT COUNT(*) FROM item")
        count = cursor.fetchone()[0]
        if count > 0:
            print(f"Warning: Table 'item' already has {count} rows. Deleting existing rows before insertion...")
            cursor.execute("DELETE FROM item")
            
        cursor.execute(sql)
        conn.commit()
        print(f"Successfully inserted {cursor.rowcount} items.")
        conn.close()
    except Exception as e:
        print(f"Error during insertion: {e}")

if __name__ == "__main__":
    insert_seed_data()
