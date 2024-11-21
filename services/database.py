import aiosqlite
from data.settings import DB_PATH

async def create_tables():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript('''
            CREATE TABLE IF NOT EXISTS jobs (
                job_id INTEGER PRIMARY KEY AUTOINCREMENT,
                town_id INTEGER,
                job_name TEXT,
                job_topic TEXT
            );
            CREATE TABLE IF NOT EXISTS ranks (
                rank_id INTEGER PRIMARY KEY AUTOINCREMENT,
                town_id INTEGER,
                points_required INTEGER
            );
            CREATE TABLE IF NOT EXISTS towns (
                guild_id INTEGER PRIMARY KEY AUTOINCREMENT,
                town_role_id INTEGER,
                town_name TEXT,
                town_topic TEXT
            );
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                rank_id INTEGER,
                town_id INTEGER,
                job_id INTEGER,
                points INTEGER DEFAULT 0,
                FOREIGN KEY (rank_id) REFERENCES ranks(rank_id)
                FOREIGN KEY (town_id) REFERENCES towns(town_id)
                FOREIGN KEY (job_id) REFERENCES towns(job_id)
            );
        ''')

        await db.commit()
