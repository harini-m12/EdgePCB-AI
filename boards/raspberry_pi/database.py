import sqlite3
import json

from pathlib import Path

BASE_DIR = Path(__file__).parent

DB_PATH = BASE_DIR / "inspection.db"


def initialize_database():

    conn = sqlite3.connect(DB_PATH)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS inspections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            inspection_id INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            status TEXT,
            severity TEXT,
            defect_count INTEGER,
            defects TEXT,
            guidance TEXT
        )
    """)

    conn.commit()
    conn.close()


def save_inspection(data, guidance):

    conn = sqlite3.connect(DB_PATH)

    conn.execute("""
        INSERT INTO inspections (
            inspection_id,
            status,
            severity,
            defect_count,
            defects,
            guidance
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        data.get("id"),
        data.get("status"),
        data.get("severity"),
        data.get("count", 0),
        json.dumps(data.get("defects", [])),
        guidance
    ))

    conn.commit()
    conn.close()


def get_inspections(limit=100):

    conn = sqlite3.connect(DB_PATH)

    conn.row_factory = sqlite3.Row

    rows = conn.execute("""
        SELECT *
        FROM inspections
        ORDER BY id DESC
        LIMIT ?
    """, (limit,)).fetchall()

    conn.close()

    return [dict(row) for row in rows]