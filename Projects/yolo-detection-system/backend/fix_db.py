import sqlite3
import os

db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 检查 knowledge 表现有字段
cursor.execute("PRAGMA table_info(knowledge)")
columns = [row[1] for row in cursor.fetchall()]
print(f"现有字段: {columns}")

# 添加缺失字段
new_columns = [
    ('status', 'VARCHAR(20) DEFAULT "active"'),
    ('uploader_id', 'INTEGER'),
    ('file_path', 'VARCHAR(500)')
]

for col_name, col_type in new_columns:
    if col_name not in columns:
        cursor.execute(f"ALTER TABLE knowledge ADD COLUMN {col_name} {col_type}")
        print(f"已添加字段: {col_name}")
    else:
        print(f"字段已存在: {col_name}")

conn.commit()
conn.close()
print("数据库修复完成")