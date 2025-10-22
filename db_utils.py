import sqlite3
from datetime import datetime

DB_NAME = "conversations.db"

# --- Inicjalizacja bazy danych ---
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Tabela rozmów
    c.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            personality TEXT,
            model TEXT,
            memory_mode TEXT,
            language TEXT,
            created_at TEXT
        )
    """)
    # Tabela wiadomości
    c.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id INTEGER,
            role TEXT,
            content TEXT,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()

# --- Tworzenie nowej rozmowy ---
def create_conversation(name, personality, model, memory_mode, language):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        INSERT INTO conversations (name, personality, model, memory_mode, language, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (name, personality, model, memory_mode, language, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    convo_id = c.lastrowid
    conn.close()
    return convo_id

# --- Pobranie listy rozmów ---
def list_conversations():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id, name FROM conversations ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()
    return rows

# --- Pobranie wiadomości dla danej rozmowy ---
def get_messages(conversation_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT role, content FROM messages WHERE conversation_id = ? ORDER BY id ASC", (conversation_id,))
    rows = [{"role": r[0], "content": r[1]} for r in c.fetchall()]
    conn.close()
    return rows

# --- Zapis wiadomości ---
def save_message(conversation_id, role, content):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        INSERT INTO messages (conversation_id, role, content, created_at)
        VALUES (?, ?, ?, ?)
    """, (conversation_id, role, content, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()

# --- Pobranie szczegółów rozmowy ---
def get_conversation(conversation_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM conversations WHERE id = ?", (conversation_id,))
    row = c.fetchone()
    conn.close()
    return row

# --- Aktualizacja nazwy rozmowy ---
def update_conversation_name(conversation_id, new_name):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE conversations SET name = ? WHERE id = ?", (new_name, conversation_id))
    conn.commit()
    conn.close()


