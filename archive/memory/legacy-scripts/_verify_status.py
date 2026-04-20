import sqlite3
conn = sqlite3.connect('memory/database/optimized_memory.db')
cur = conn.cursor()
print('episodes', cur.execute('select count(*) from episodes').fetchone()[0])
print('vectors', cur.execute('select count(*) from memory_vectors').fetchone()[0])
print('bad', cur.execute("select count(*) from episodes where content = ?", ('娴嬭瘯缁熶竴璁板繂鍐欏叆',)).fetchone()[0])
conn.close()
