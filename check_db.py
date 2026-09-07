import sqlite3
conn = sqlite3.connect("bot.db")
cursor = conn.cursor()
cursor.execute("SELECT id, status FROM orders")
rows = cursor.fetchall()
for row in rows:
    print(f"Заявка #{row[0]}, статус: '{row[1]}'")
conn.close()