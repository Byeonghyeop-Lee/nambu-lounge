from datetime import datetime
from modules.db import get_connection


def get_all_posts(sort='latest'):
    conn = get_connection()
    cursor = conn.cursor()
    order = 'comment_count DESC, p.created_at DESC' if sort == 'popular' else 'p.created_at DESC'
    cursor.execute(f'''
        SELECT p.*, COUNT(c.id) AS comment_count
        FROM posts p
        LEFT JOIN comments c ON c.post_id = p.id
        GROUP BY p.id
        ORDER BY {order}
    ''')
    posts = cursor.fetchall()
    conn.close()
    return posts


def get_post(post_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM posts WHERE id = %s', (post_id,))
    post = cursor.fetchone()
    conn.close()
    return post


def create_post(title, content, nickname='익명'):
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    cursor.execute(
        'INSERT INTO posts (title, content, nickname, created_at) VALUES (%s, %s, %s, %s) RETURNING id',
        (title, content, nickname, now)
    )
    post_id = cursor.fetchone()['id']
    conn.commit()
    conn.close()
    return post_id


def delete_post(post_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM posts WHERE id = %s', (post_id,))
    conn.commit()
    conn.close()
