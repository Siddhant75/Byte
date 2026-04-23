import sqlite3
import os

# Create an absolute path relative to this file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "pet_state.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Drop old table to migrate to new schema
    # cursor.execute('DROP TABLE IF EXISTS pet_stats') 
    
    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pet_stats (
            id INTEGER PRIMARY KEY,
            name TEXT,
            level INTEGER DEFAULT 1,
            focus_sessions_completed INTEGER DEFAULT 0,
            total_focus_minutes INTEGER DEFAULT 0,
            current_activity TEXT DEFAULT 'idle',
            hunger INTEGER DEFAULT 100,
            energy INTEGER DEFAULT 100,
            happiness INTEGER DEFAULT 100
        )
    ''')

    # Migration: Add columns if they don't exist (for existing databases)
    try:
        cursor.execute("ALTER TABLE pet_stats ADD COLUMN hunger INTEGER DEFAULT 100")
    except sqlite3.OperationalError: pass
    try:
        cursor.execute("ALTER TABLE pet_stats ADD COLUMN energy INTEGER DEFAULT 100")
    except sqlite3.OperationalError: pass
    try:
        cursor.execute("ALTER TABLE pet_stats ADD COLUMN happiness INTEGER DEFAULT 100")
    except sqlite3.OperationalError: pass
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT,
            message TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Insert default row if empty
    cursor.execute("SELECT COUNT(*) FROM pet_stats")
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
            INSERT INTO pet_stats (id, name, level, focus_sessions_completed, total_focus_minutes, current_activity, hunger, energy, happiness)
            VALUES (1, 'Byte', 1, 0, 0, 'idle', 100, 100, 100)
        ''')
    
    conn.commit()
    conn.close()

def get_stats():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pet_stats WHERE id = 1")
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def log_focus_session(minutes: int, completed: bool = False):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get current stats
    cursor.execute("SELECT focus_sessions_completed, total_focus_minutes FROM pet_stats WHERE id = 1")
    row = cursor.fetchone()
    
    # Only increment session count if the timer actually finished
    new_sessions = row['focus_sessions_completed']
    if completed:
        new_sessions += 1
        
    new_minutes = row['total_focus_minutes'] + minutes
    
    # Calculate level: +1 level every 10 sessions
    new_level = (new_sessions // 10) + 1
    
    cursor.execute('''
        UPDATE pet_stats 
        SET focus_sessions_completed = ?, 
            total_focus_minutes = ?,
            level = ?
        WHERE id = 1
    ''', (new_sessions, new_minutes, new_level))
    
    conn.commit()
    conn.close()
    return {"level": new_level, "sessions": new_sessions, "minutes": new_minutes}

def update_activity(activity: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE pet_stats SET current_activity = ? WHERE id = 1", (activity,))
    conn.commit()
    conn.close()
    return {"activity": activity}

def decay_stats():
    """Reduces hunger, energy, and happiness periodically."""
    conn = get_db_connection()
    cursor = conn.cursor()
    # Decrease stats but clamp at 0
    cursor.execute('''
        UPDATE pet_stats 
        SET hunger = MAX(0, hunger - 5),
            energy = MAX(0, energy - 2),
            happiness = MAX(0, happiness - 3)
        WHERE id = 1
    ''')
    conn.commit()
    conn.close()
    return get_stats()

def add_history(sender: str, message: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO chat_history (sender, message) VALUES (?, ?)", (sender, message))
    conn.commit()
    conn.close()

def get_history():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM chat_history ORDER BY timestamp ASC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def delete_history_item(item_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM chat_history WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()

def clear_all_history():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM chat_history")
    conn.commit()
    conn.close()
