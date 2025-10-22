import sqlite3
from datetime import datetime

DB_NAME = "conversations.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
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

def create_conversation(name, personality, model, memory_mode, language):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        INSERT INTO conversations (name, personality, model, memory_mode, language, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (name, personality, model, memory_mode, language, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    convo_id = c.lastrowid
    conn.commit()
    conn.close()
    return convo_id



