import sqlite3

DB_NAME = "conversations.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    personality TEXT,
                    model TEXT,
                    memory_mode TEXT,
                    language TEXT
                )""")
    c.execute("""CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id INTEGER,
                    role TEXT,
                    content TEXT
                )""")
    conn.commit()
    conn.close()

def create_conversation(name, personality, model, memory_mode, language):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO conversations (name, personality, model, memory_mode, language) VALUES (?, ?, ?, ?, ?)",
              (name, personality, model, memory_mode, language))
    convo_id = c.lastrowid
    conn.commit()
    conn.close()
    return convo_id

def list_conversations():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id, name FROM conversations ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()
    return rows

def get_conversation(convo_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM conversations WHERE id=?", (convo_id,))
    row = c.fetchone()
    conn.close()
    return row

def save_message(convo_id, role, content):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO messages (conversation_id, role, content) VALUES (?, ?, ?)",
              (convo_id, role, content))
    conn.commit()
    conn.close()

def get_messages(convo_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT role, content FROM messages WHERE conversation_id=?", (convo_id,))
    rows = [{"role": r[0], "content": r[1]} for r in c.fetchall()]
    conn.close()
    return rows
