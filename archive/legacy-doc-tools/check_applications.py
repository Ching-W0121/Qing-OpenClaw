import sqlite3
from datetime import datetime

conn = sqlite3.connect('qing-agent/qing_jobs.db')
cursor = conn.cursor()

# 查询投递总数
cursor.execute('SELECT COUNT(*) FROM applications')
total = cursor.fetchone()[0]
print(f'=== 投递数据统计 ===')
print(f'投递总数：{total}')

# 查询最近投递记录
cursor.execute('''
    SELECT company, position, salary, platform, applied_date, status 
    FROM applications 
    ORDER BY applied_date DESC 
    LIMIT 20
''')
rows = cursor.fetchall()

print(f'\n=== 最近 20 条投递记录 ===')
for r in rows:
    print(f'公司：{r[0]}')
    print(f'职位：{r[1]}')
    print(f'薪资：{r[2]}')
    print(f'平台：{r[3]}')
    print(f'日期：{r[4]}')
    print(f'状态：{r[5]}')
    print('---')

# 按平台统计
cursor.execute('SELECT platform, COUNT(*) FROM applications GROUP BY platform')
platform_stats = cursor.fetchall()
print(f'\n=== 按平台统计 ===')
for p in platform_stats:
    print(f'{p[0]}: {p[1]}条')

conn.close()
