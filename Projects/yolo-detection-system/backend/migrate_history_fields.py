"""为 detection_history 表补充 class_names / max_confidence 字段并回填旧数据

用法：python migrate_history_fields.py
"""
import json
import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app.db')

NEW_COLUMNS = [
    ('class_names', 'VARCHAR(500)'),
    ('max_confidence', 'FLOAT'),
]


def add_columns(cursor) -> None:
    """添加缺失字段（已存在则跳过）

    Args:
        cursor: sqlite3 游标
    """
    cursor.execute('PRAGMA table_info(detection_history)')
    existing = [row[1] for row in cursor.fetchall()]
    print(f'现有字段: {existing}')

    for column_name, column_type in NEW_COLUMNS:
        if column_name in existing:
            print(f'字段已存在，跳过: {column_name}')
        else:
            cursor.execute(
                f'ALTER TABLE detection_history ADD COLUMN {column_name} {column_type}'
            )
            print(f'已添加字段: {column_name}')


def backfill(cursor) -> int:
    """按 detection_result 回填冗余筛选字段

    Args:
        cursor: sqlite3 游标

    Returns:
        int: 回填的记录数
    """
    cursor.execute(
        'SELECT id, detection_result FROM detection_history '
        'WHERE detection_result IS NOT NULL'
    )
    rows = cursor.fetchall()
    updated = 0

    for history_id, raw_result in rows:
        try:
            result = json.loads(raw_result)
        except (TypeError, ValueError):
            print(f'记录 {history_id} 的 detection_result 无法解析，跳过')
            continue

        class_summary = result.get('class_summary') or {}
        class_names = ','.join(class_summary.keys()) or None
        confidences = [
            det.get('confidence') for det in result.get('detections') or []
            if isinstance(det.get('confidence'), (int, float))
        ]
        max_confidence = max(confidences) if confidences else None

        cursor.execute(
            'UPDATE detection_history SET class_names = ?, max_confidence = ? WHERE id = ?',
            (class_names, max_confidence, history_id)
        )
        updated += 1

    return updated


def main() -> None:
    """执行迁移"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    add_columns(cursor)
    updated = backfill(cursor)

    conn.commit()
    conn.close()
    print(f'数据库迁移完成，回填 {updated} 条历史记录')


if __name__ == '__main__':
    main()