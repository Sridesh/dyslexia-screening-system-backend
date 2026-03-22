import sqlite3
import os
import sys
import json

# Add current directory to path so we can import app if needed
sys.path.append(os.getcwd())

def reset_items():
    DB_FILE = "sql_app.db"
    
    print(f"--- RESET SCRIPT STARTING (DB: {DB_FILE}) ---")
    
    if not os.path.exists(DB_FILE):
        print(f"CRITICAL ERROR: {DB_FILE} not found in {os.getcwd()}")
        return

    # Helper to create JSON options in the format frontend expects: [{"id": "...", "text": "..."}]
    def fmt_options(opts_list):
        if not opts_list: return None
        return json.dumps([{"id": o.lower(), "text": o.capitalize()} for o in opts_list])

    # Precise format for complex options
    def complex_options(opts_dict_list):
        return json.dumps(opts_dict_list)

    items_data = [
      (1,  'phonemic_awareness', -2.0, 8.0,  'audio_text',   'Do these words rhyme? CAT - HAT',
           NULL, 'yes', fmt_options(['yes', 'no']), TRUE),
      (2,  'phonemic_awareness', -1.5, 8.0,  'audio_text',   'Do these words rhyme? TREE - BEE',
           NULL, 'yes', fmt_options(['yes', 'no']), TRUE),
      (3,  'phonemic_awareness', -1.0, 10.0, 'audio_text',   'Which word starts with the same sound as SUN?',
           NULL, 'sock', fmt_options(['sock', 'ball', 'tree']), TRUE),
      (4,  'phonemic_awareness', -0.5, 10.0, 'audio_text',   'Put these sounds together to make a word: /d/ /o/ /g/',
           NULL, 'dog', fmt_options(['dog', 'dig', 'bag', 'dot']), TRUE),
      (5,  'phonemic_awareness',  0.0, 12.0, 'audio_text',   'Put these sounds together to make a word: /s/ /t/ /o/ /p/',
           NULL, 'stop', fmt_options(['stop', 'step', 'top', 'spot']), TRUE),
      (6,  'phonemic_awareness',  0.5, 12.0, 'audio_text',   'How many sounds do you hear in the word FISH?',
           NULL, '3', fmt_options(['2', '3', '4', '5']), TRUE),
      (7,  'phonemic_awareness',  1.0, 15.0, 'audio_text',   'Say SPOT without the /s/ sound. What word is left?',
           NULL, 'pot', fmt_options(['pot', 'top', 'sot', 'pop']), TRUE),
      (8,  'phonemic_awareness',  1.5, 15.0, 'audio_text',   'Say CLAP without the /l/ sound. What word is left?',
           NULL, 'cap', fmt_options(['cap', 'lap', 'tap', 'clap']), TRUE),
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
      (16, 'ran',                 1.5, 8.0,  'image',        'Name these items left to right: A 3 B 5',
           'images/ran/alternating_A3B5.png', 'A 3 B 5', NULL, TRUE),
      (17, 'object_recognition', -2.0, 8.0,  'image_choice', 'Which picture shows a DOG?',
           'images/obj/dog_cat_bird_fish.png', 'A', complex_options([{"id":"A","text":"A"},{"id":"B","text":"B"},{"id":"C","text":"C"},{"id":"D","text":"D"}]), TRUE),
      (18, 'object_recognition', -1.5, 8.0,  'image_choice', 'Which shape is DIFFERENT?',
           'images/obj/three_circles_one_square.png', 'D', complex_options([{"id":"A","text":"A"},{"id":"B","text":"B"},{"id":"C","text":"C"},{"id":"D","text":"D"}]), TRUE),
      (19, 'object_recognition', -1.0, 10.0, 'image_choice', 'Which arrow points to the RIGHT?',
           'images/obj/arrows_directions.png', 'B', complex_options([{"id":"A","text":"A"},{"id":"B","text":"B"},{"id":"C","text":"C"},{"id":"D","text":"D"}]), TRUE),
      (20, 'object_recognition', -0.5, 10.0, 'image_choice', 'Find the matching picture',
           'images/obj/shape_match_easy.png', 'C', complex_options([{"id":"A","text":"A"},{"id":"B","text":"B"},{"id":"C","text":"C"},{"id":"D","text":"D"}]), TRUE),
      (21, 'object_recognition',  0.0, 10.0, 'image_choice', 'Which one is the letter b?',
           'images/obj/b_d_p_q.png', 'A', complex_options([{"id":"A","text":"b"},{"id":"B","text":"d"},{"id":"C","text":"p"},{"id":"D","text":"q"}]), TRUE),
      (22, 'object_recognition',  0.5, 12.0, 'image_choice', 'Which picture is the MIRROR IMAGE?',
           'images/obj/mirror_image_moderate.png', 'B', complex_options([{"id":"A","text":"A"},{"id":"B","text":"B"},{"id":"C","text":"C"},{"id":"D","text":"D"}]), TRUE),
      (23, 'object_recognition',  1.0, 15.0, 'image_choice', 'Which symbol sequence matches?',
           'images/obj/symbol_sequence_hard.png', 'C', complex_options([{"id":"A","text":"A"},{"id":"B","text":"B"},{"id":"C","text":"C"},{"id":"D","text":"D"}]), TRUE),
      (24, 'object_recognition',  1.5, 15.0, 'image_choice', 'Find the hidden shape',
           'images/obj/embedded_figure.png', 'B', complex_options([{"id":"A","text":"A"},{"id":"B","text":"B"},{"id":"C","text":"C"},{"id":"D","text":"D"}]), TRUE),
      (25, 'phonemic_awareness', -0.25, 10.0, 'audio_text',   'Put these sounds together: /f/ /i/ /sh/',
           NULL, 'fish', fmt_options(['fish', 'fit', 'dish', 'fig']), TRUE),
      (26, 'phonemic_awareness',  0.25, 12.0, 'audio_text',   'How many sounds in the word LAMP?',
           NULL, '4', fmt_options(['3', '4', '5', '2']), TRUE),
      (27, 'ran',                -0.25, 5.0,  'image',        'Name this letter as fast as you can',
           'images/ran/letter_S.png', 'S', NULL, TRUE),
      (28, 'ran',                 0.25, 5.0,  'image',        'Name this number as fast as you can',
           'images/ran/number_4.png', '4', NULL, TRUE),
      (29, 'object_recognition', -0.25, 10.0, 'image_choice', 'Which letter faces the same way?',
           'images/obj/letter_direction_easy.png', 'C', complex_options([{"id":"A","text":"A"},{"id":"B","text":"B"},{"id":"C","text":"C"},{"id":"D","text":"D"}]), TRUE),
      (30, 'object_recognition',  0.25, 12.0, 'image_choice', 'Find the pair that matches exactly',
           'images/obj/pair_match_moderate.png', 'A', complex_options([{"id":"A","text":"A"},{"id":"B","text":"B"},{"id":"C","text":"C"},{"id":"D","text":"D"}]), TRUE)
    ]
    
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        print("Step 1: Clearing existing items...")
        cursor.execute("DELETE FROM item")
        
        print("Step 2: Inserting 30 clean items with correct options format...")
        insert_query = """
        INSERT INTO item (id, module, difficulty, max_time_s, prompt_type, prompt_text, 
                          prompt_media, correct_option, options_json, is_active)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        cursor.executemany(insert_query, items_data)
        
        print("Step 3: Committing changes...")
        conn.commit()
        print(f"SUCCESS: Reset database populated with {cursor.rowcount} items.")
        
        cursor.execute("SELECT COUNT(*) FROM item")
        count = cursor.fetchone()[0]
        print(f"VERIFICATION: Final database count is {count}.")
        
        conn.close()
    except Exception as e:
        print(f"EXCEPTION DURING EXECUTION: {e}")
        sys.exit(1)

if __name__ == "__main__":
    reset_items()
