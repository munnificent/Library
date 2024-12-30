import sqlite3


DATABASE = 'library.db'

# ====== Подключение к БД ======
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# ====== Инициализация БД (создание, если нет) ======
def init_db():
        conn = get_db_connection()
        conn.execute('''CREATE TABLE books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            direction TEXT NOT NULL,
            material_type TEXT NOT NULL,
            year INTEGER,
            language TEXT,
            availability TEXT,
            image_path TEXT,    -- 'uploads/filename.jpg'
            file_path TEXT      -- 'uploads/filename.pdf'
        );''')
        conn.commit()
        conn.close()
        print("Создана новая база данных library.db")

init_db()

