import sqlite3

def create_connection(db_file):
    """Create a database connection to the SQLite database specified by db_file."""
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except sqlite3.Error as e:
        print(e)
    return conn

def create_table(conn):
    """Create a table if it doesn't exist."""
    create_table_sql = '''CREATE TABLE IF NOT EXISTS chat_history (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            question TEXT NOT NULL,
                            answer TEXT NOT NULL
                          );'''
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except sqlite3.Error as e:
        print(e)

def insert_chat_history(conn, question, answer):
    """Insert a new question and answer into the chat_history table."""
    sql = '''INSERT INTO chat_history(question, answer) VALUES(?, ?)'''
    cur = conn.cursor()
    cur.execute(sql, (question, answer))
    conn.commit()
    return cur.lastrowid

def fetch_chat_history(conn):
    """Fetch all rows from the chat_history table."""
    cur = conn.cursor()
    cur.execute("SELECT question, answer FROM chat_history")
    rows = cur.fetchall()
    return rows
