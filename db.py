import sqlite3
from datetime import datetime
from config import DATABASE_PATH


def init_db():
    """Initialize database with required tables."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS spam_patterns (
            id INTEGER PRIMARY KEY,
            group_id INTEGER NOT NULL,
            pattern_text TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_messages (
            id INTEGER PRIMARY KEY,
            group_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            message_count INTEGER DEFAULT 0,
            blocked BOOLEAN DEFAULT 0,
            UNIQUE(group_id, user_id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admin_logs (
            id INTEGER PRIMARY KEY,
            group_id INTEGER NOT NULL,
            action TEXT NOT NULL,
            details TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()


def add_spam_pattern(group_id, text, embedding=None):
    """Add a spam pattern to the database."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO spam_patterns (group_id, pattern_text)
        VALUES (?, ?)
    ''', (group_id, text))

    conn.commit()
    conn.close()


def get_spam_patterns(group_id):
    """Retrieve all spam patterns for a group."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT id, pattern_text FROM spam_patterns
        WHERE group_id = ?
    ''', (group_id,))

    patterns = cursor.fetchall()
    conn.close()

    result = []
    for pattern_id, text in patterns:
        result.append((pattern_id, text, None))

    return result


def get_user_message_count(group_id, user_id):
    """Get the message count for a user in a group."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT message_count FROM user_messages
        WHERE group_id = ? AND user_id = ?
    ''', (group_id, user_id))

    result = cursor.fetchone()
    conn.close()

    return result[0] if result else 0


def increment_user_message_count(group_id, user_id):
    """Increment the message count for a user in a group."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO user_messages (group_id, user_id, message_count)
        VALUES (?, ?, 1)
        ON CONFLICT(group_id, user_id) DO UPDATE SET
        message_count = message_count + 1
    ''', (group_id, user_id))

    conn.commit()
    conn.close()


def log_admin_action(group_id, action, details=None):
    """Log an admin action."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO admin_logs (group_id, action, details)
        VALUES (?, ?, ?)
    ''', (group_id, action, details))

    conn.commit()
    conn.close()


def is_user_blocked(group_id, user_id):
    """Check if a user is blocked in a group."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT blocked FROM user_messages
        WHERE group_id = ? AND user_id = ?
    ''', (group_id, user_id))

    result = cursor.fetchone()
    conn.close()

    return result[0] if result else False


def block_user(group_id, user_id):
    """Block a user in a group."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO user_messages (group_id, user_id, blocked)
        VALUES (?, ?, 1)
        ON CONFLICT(group_id, user_id) DO UPDATE SET
        blocked = 1
    ''', (group_id, user_id))

    conn.commit()
    conn.close()


def clear_spam_pattern(pattern_id):
    """Remove a spam pattern from the database."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute('DELETE FROM spam_patterns WHERE id = ?', (pattern_id,))

    conn.commit()
    conn.close()
