import aiosqlite
from config import DB_NAME

async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                role TEXT DEFAULT 'user'
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                category TEXT,
                model TEXT,
                characteristics TEXT,
                condition TEXT,
                photo_file_id TEXT,
                status TEXT DEFAULT 'new',
                price INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        await db.commit()

# ---- Users ----
async def get_user(user_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT * FROM users WHERE user_id = ?', (user_id,)) as cursor:
            return await cursor.fetchone()

async def set_user(user_id: int, username: str):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('INSERT OR IGNORE INTO users (user_id, username, role) VALUES (?, ?, "user")', (user_id, username))
        await db.commit()

async def set_role(user_id: int, role: str):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('UPDATE users SET role = ? WHERE user_id = ?', (role, user_id))
        await db.commit()

async def get_all_users():
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT user_id, username, role FROM users') as cursor:
            return await cursor.fetchall()

async def get_managers():
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT user_id, username FROM users WHERE role = "manager"') as cursor:
            return await cursor.fetchall()

# ---- Orders ----
async def add_order(user_id, category, model, characteristics, condition, photo_file_id):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute('''
            INSERT INTO orders (user_id, category, model, characteristics, condition, photo_file_id)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, category, model, characteristics, condition, photo_file_id))
        await db.commit()
        return cursor.lastrowid

async def get_order(order_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT * FROM orders WHERE id = ?', (order_id,)) as cursor:
            return await cursor.fetchone()

async def get_orders(limit: int, offset: int):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT * FROM orders ORDER BY created_at DESC LIMIT ? OFFSET ?', (limit, offset)) as cursor:
            return await cursor.fetchall()

async def get_orders_by_status(status: str):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT * FROM orders WHERE status = ?', (status,)) as cursor:
            return await cursor.fetchall()

async def update_order_status(order_id: int, new_status: str, price: int = None):
    async with aiosqlite.connect(DB_NAME) as db:
        if price is not None:
            await db.execute('UPDATE orders SET status = ?, price = ? WHERE id = ?', (new_status, price, order_id))
        else:
            await db.execute('UPDATE orders SET status = ? WHERE id = ?', (new_status, order_id))
        await db.commit()

async def get_all_orders():
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT * FROM orders ORDER BY created_at DESC') as cursor:
            return await cursor.fetchall()

async def count_users():
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT COUNT(*) FROM users') as cursor:
            return (await cursor.fetchone())[0]

async def count_orders():
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT COUNT(*) FROM orders') as cursor:
            return (await cursor.fetchone())[0]

async def count_orders_by_status():
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT status, COUNT(*) FROM orders GROUP BY status') as cursor:
            rows = await cursor.fetchall()
            return {row[0]: row[1] for row in rows}