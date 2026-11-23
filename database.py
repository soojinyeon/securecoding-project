import os
import sqlite3

import config


def get_connection():
    os.makedirs(os.path.dirname(config.DB_PATH), exist_ok=True)
    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def query(sql, one=False):
    conn = get_connection()
    try:
        cur = conn.execute(sql)
        rows = cur.fetchall()
        conn.commit()
        return (rows[0] if rows else None) if one else rows
    finally:
        conn.close()


def query_safe(sql, params=(), one=False):
    conn = get_connection()
    try:
        cur = conn.execute(sql, params)
        rows = cur.fetchall()
        conn.commit()
        return (rows[0] if rows else None) if one else rows
    finally:
        conn.close()


def execute_safe(sql, params=()):
    conn = get_connection()
    try:
        cur = conn.execute(sql, params)
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def execute_count(sql, params=()):
    """파라미터 바인딩으로 실행하고 영향받은 행 수를 반환한다."""
    conn = get_connection()
    try:
        cur = conn.execute(sql, params)
        conn.commit()
        return cur.rowcount
    finally:
        conn.close()


def init_db():
    os.makedirs(os.path.dirname(config.DB_PATH), exist_ok=True)
    conn = get_connection()
    try:
        with open(config.SCHEMA_PATH, "r", encoding="utf-8") as f:
            conn.executescript(f.read())
        conn.commit()
    finally:
        conn.close()
