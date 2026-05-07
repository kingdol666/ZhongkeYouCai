#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SQLite 数据库模块：历史数据记录的增删改查
"""

import os
import sqlite3
from datetime import datetime
from typing import Any

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "history.db")


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """初始化数据库表"""
    with _connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                saved_at TEXT NOT NULL,
                csv_path TEXT NOT NULL,
                image_path TEXT NOT NULL,
                save_dir TEXT NOT NULL,
                is_abnormal INTEGER NOT NULL DEFAULT 0,
                remarks TEXT DEFAULT ''
            )
        """)
        conn.commit()


def insert_record(csv_path: str, image_path: str, save_dir: str,
                  is_abnormal: int = 0, remarks: str = "") -> int:
    """插入一条历史记录，返回新记录的 id"""
    with _connect() as conn:
        cur = conn.execute(
            "INSERT INTO history (saved_at, csv_path, image_path, save_dir, is_abnormal, remarks) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), csv_path, image_path, save_dir,
             is_abnormal, remarks)
        )
        conn.commit()
        return cur.lastrowid


def query_records(search: str = "", order_desc: bool = True,
                  is_abnormal: int | None = None,
                  date_from: str = "", date_to: str = "") -> list[dict[str, Any]]:
    """查询记录，支持按关键词、异常状态、日期范围筛选"""
    conditions = []
    params: list[Any] = []

    if search:
        conditions.append(
            "(csv_path LIKE ? OR image_path LIKE ? OR save_dir LIKE ? OR remarks LIKE ?)")
        params.extend([f"%{search}%"] * 4)

    if is_abnormal is not None:
        conditions.append("is_abnormal = ?")
        params.append(is_abnormal)

    if date_from:
        conditions.append("saved_at >= ?")
        params.append(date_from)
    if date_to:
        conditions.append("saved_at <= ?")
        params.append(date_to + " 23:59:59")

    where = (" WHERE " + " AND ".join(conditions)) if conditions else ""
    order = " ORDER BY id " + ("DESC" if order_desc else "ASC")

    with _connect() as conn:
        rows = conn.execute("SELECT * FROM history" + where + order, params).fetchall()
        return [dict(r) for r in rows]


def get_record(record_id: int) -> dict[str, Any] | None:
    with _connect() as conn:
        row = conn.execute("SELECT * FROM history WHERE id = ?", (record_id,)).fetchone()
        return dict(row) if row else None


def update_record(record_id: int, is_abnormal: int | None = None, remarks: str | None = None):
    """更新记录的异常标记和/或备注"""
    with _connect() as conn:
        if is_abnormal is not None:
            conn.execute("UPDATE history SET is_abnormal = ? WHERE id = ?", (is_abnormal, record_id))
        if remarks is not None:
            conn.execute("UPDATE history SET remarks = ? WHERE id = ?", (remarks, record_id))
        conn.commit()


def delete_record(record_id: int):
    with _connect() as conn:
        conn.execute("DELETE FROM history WHERE id = ?", (record_id,))
        conn.commit()


def delete_records(record_ids: list[int]):
    with _connect() as conn:
        conn.executemany("DELETE FROM history WHERE id = ?", [(i,) for i in record_ids])
        conn.commit()
