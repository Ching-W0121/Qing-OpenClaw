import sqlite3

conn = sqlite3.connect('C:/Users/TR/.openclaw/workspace/qing-agent/data/qing_agent.db')
cursor = conn.cursor()

# 查看所有表
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print('=== 数据库表 ===')
for t in tables:
    print(f'表名：{t[0]}')
    cursor.execute(f"SELECT COUNT(*) FROM {t[0]}")
    count = cursor.fetchone()[0]
    print(f'  记录数：{count}')

conn.close()
