from datetime import datetime
from modules.db import get_connection


def get_comments(post_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        'SELECT * FROM comments WHERE post_id = %s ORDER BY created_at ASC',
        (post_id,)
    )
    comments = cursor.fetchall()
    conn.close()
    return comments


def create_comment(post_id, content, nickname='익명'):
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    cursor.execute(
        'INSERT INTO comments (post_id, content, nickname, created_at) VALUES (%s, %s, %s, %s) RETURNING id',
        (post_id, content, nickname, now)
    )
    comment_id = cursor.fetchone()['id']
    conn.commit()
    conn.close()
    return comment_id


def delete_comment(comment_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM comments WHERE id = %s', (comment_id,))
    conn.commit()
    conn.close()
