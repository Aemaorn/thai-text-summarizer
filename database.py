import sqlite3

def init_db():
    conn = sqlite3.connect('summarizer.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS summaries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            original_text TEXT,
            summary TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def save_summary(original, summary):
    conn = sqlite3.connect('summarizer.db')
    c = conn.cursor()
    c.execute('INSERT INTO summaries (original_text, summary) VALUES (?, ?)', (original, summary))
    conn.commit()
    conn.close()

def get_all_summaries():
    conn = sqlite3.connect('summarizer.db')
    c = conn.cursor()
    c.execute('SELECT id, original_text, summary, created_at FROM summaries ORDER BY created_at DESC')
    rows = c.fetchall()
    conn.close()
    return rows
