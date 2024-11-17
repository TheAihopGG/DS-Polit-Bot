import aiosqlite
from data.settings import DB_PATH

async def create_tables():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS jobs (
                job_id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT,
                guild_id INTEGER
            );
        ''')

        await db.execute('''
            CREATE TABLE IF NOT EXISTS ranks (
                rank_id INTEGER PRIMARY KEY AUTOINCREMENT,
                points_required INTEGER NOT NULL,
                guild_id INTEGER
            );
        ''')

        await db.execute('''
            CREATE TABLE IF NOT EXISTS towns (
                guild_id INTEGER PRIMARY KEY AUTOINCREMENT,
                town_name TEXT,
                topic TEXT
            );
        ''')

        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER,
                username TEXT NOT NULL,
                points INTEGER DEFAULT 0,
                rank_id INTEGER,
                town_id INTEGER,
                jobs JSON DEFAULT [], 
                FOREIGN KEY (rank_id) REFERENCES ranks(rank_id)
                FOREIGN KEY (rank_id) REFERENCES ranks(rank_id)
            );
        ''')

        await db.commit()
