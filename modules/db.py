import os
import psycopg2
import psycopg2.extras
import psycopg2.pool
import streamlit as st


@st.cache_resource
def _get_pool():
    return psycopg2.pool.ThreadedConnectionPool(
        1, 5, dsn=os.getenv('DATABASE_URL')
    )


def get_connection():
    pool = _get_pool()
    conn = pool.getconn()
    conn.cursor_factory = psycopg2.extras.RealDictCursor

    def _return_to_pool():
        pool.putconn(conn)

    conn.close = _return_to_pool
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            nickname TEXT NOT NULL DEFAULT '익명',
            created_at TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS comments (
            id SERIAL PRIMARY KEY,
            post_id INTEGER NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
            content TEXT NOT NULL,
            nickname TEXT NOT NULL DEFAULT '익명',
            created_at TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS suggestions (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL,
            is_read INTEGER DEFAULT 0
        )
    ''')

    conn.commit()
    conn.close()
