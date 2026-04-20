import sqlite3

conn = sqlite3.connect('C:/Users/TR/.openclaw/workspace/qing-agent/qing_jobs.db')
cursor = conn.cursor()

# 查看所有表
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print('=== 数据库表 ===')
for t in tables:
    print(f'表名：{t[0]}')

# 查看 jobs 表结构
cursor.execute("PRAGMA table_info(jobs)")
columns = cursor.fetchall()
print('\n=== jobs 表结构 ===')
for col in columns:
    print(f'{col[1]} ({col[2]})')

# 查看投递记录
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%apply%'")
apply_tables = cursor.fetchall()
print('\n=== 投递相关表 ===')
for t in apply_tables:
    print(f'表名：{t[0]}')

conn.close()
