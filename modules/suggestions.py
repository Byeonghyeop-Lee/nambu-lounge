from datetime import datetime
from modules.db import get_connection


def create_suggestion(title, content):
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    cursor.execute(
        'INSERT INTO suggestions (title, content, created_at) VALUES (%s, %s, %s)',
        (title, content, now)
    )
    conn.commit()
    conn.close()


def get_all_suggestions():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM suggestions ORDER BY created_at DESC')
    suggestions = cursor.fetchall()
    conn.close()
    return suggestions


def mark_as_read(suggestion_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE suggestions SET is_read = 1 WHERE id = %s', (suggestion_id,))
    conn.commit()
    conn.close()


def delete_suggestion(suggestion_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM suggestions WHERE id = %s', (suggestion_id,))
    conn.commit()
    conn.close()


def get_unread_count():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) AS cnt FROM suggestions WHERE is_read = 0')
    count = cursor.fetchone()['cnt']
    conn.close()
    return count
