import os
import sqlite3
import uuid
import shutil
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    send_from_directory,
    flash,
    session
)
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'some_secret_key_for_flask_messages'

DATABASE = 'library.db'
BACKUP_DIR = 'backups'

# ===== Подключение к БД =====
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# ===== Инициализация БД =====
def init_db():
    if not os.path.exists(DATABASE):
        conn = get_db_connection()
        # Храним категорию и подкатегорию в direction/material_type
        conn.execute('''CREATE TABLE books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            direction TEXT NOT NULL,
            material_type TEXT NOT NULL,
            year INTEGER,
            language TEXT,
            description TEXT,
            image_path TEXT,
            file_path TEXT,
            original_filename TEXT  -- <--- новое поле
        );''')
        conn.commit()
        conn.close()
        print("Создана новая база данных library.db")

    os.makedirs(os.path.join('static', 'uploads'), exist_ok=True)
    os.makedirs(BACKUP_DIR, exist_ok=True)

init_db()

# ===== Главная =====
@app.route('/')
def index():
    conn = get_db_connection()
    books = conn.execute("SELECT * FROM books").fetchall()
    conn.close()
    return render_template('index.html', books=books)

# ===== Логин / Логаут =====
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form.get('username')
        pwd = request.form.get('password')
        if user == 'admin' and pwd == 'secret':
            session['logged_in'] = True
            flash("Вы успешно вошли как админ!", "success")
            return redirect(url_for('admin'))
        else:
            flash("Неверные учетные данные!", "error")
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session['logged_in'] = False
    flash("Вы вышли из админ-панели.", "info")
    return redirect(url_for('index'))

# ===== Админ =====
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if not session.get('logged_in'):
        flash("Требуется вход в систему!", "error")
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form.get('title')
        author = request.form.get('author')
        direction = request.form.get('direction')
        material_type = request.form.get('material_type')
        year = request.form.get('year') or None
        language = request.form.get('language')
        description = request.form.get('description') or ''

        cover_file = request.files.get('cover_file')
        download_file = request.files.get('download_file')

        cover_filename = None
        download_filename = None
        original_filename = None


        # Уникальное имя обложки
        if cover_file and cover_file.filename.strip():
            basefilename = secure_filename(cover_file.filename)
            ext = os.path.splitext(basefilename)[1]
            unique_name = f"{uuid.uuid4().hex}{ext}"
            cover_filename = f"uploads/{unique_name}"
            cover_file.save(os.path.join('static', cover_filename))

        # Уникальное имя файла для скачивания
        if download_file and download_file.filename.strip():
            # Сохраняем ОРИГИНАЛЬНОЕ имя в переменную
            original_filename = download_file.filename  # То, что загрузил пользователь

            # Генерация уникального имени
            basefilename = secure_filename(download_file.filename)  # "Instrukciya.pdf"
            fn, ext = os.path.splitext(basefilename)
            if not ext:
                # Если расширения нет, допустим ставим .pdf
                ext = ".pdf"

            unique_name = f"{uuid.uuid4().hex}{ext}"
            download_filename = f"uploads/{unique_name}"
            download_file.save(os.path.join('static', download_filename))

        if not title or not author:
            flash("Поля 'Название книги' и 'Автор' обязательны!", "error")
            return redirect(url_for('admin'))

        conn = get_db_connection()
         # Далее сохраняем всё в БД
        conn.execute("""
                INSERT INTO books
                (title, author, direction, material_type, year, language, description, 
                image_path, file_path, original_filename)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                title, author, direction, material_type, year, language, description,
                cover_filename, download_filename, original_filename
            ))
        conn.commit()
        conn.close()

        flash("Книга успешно добавлена!", "success")
        return redirect(url_for('admin'))

    conn = get_db_connection()
    books = conn.execute("SELECT * FROM books").fetchall()
    conn.close()
    return render_template('admin.html', books=books)

# ===== Удаление книги =====
@app.route('/delete/<int:book_id>', methods=['POST'])
def delete_book(book_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    conn = get_db_connection()
    book = conn.execute("SELECT * FROM books WHERE id = ?", (book_id,)).fetchone()
    if book:
        if book['image_path']:
            img_path = os.path.join('static', book['image_path'])
            if os.path.exists(img_path):
                os.remove(img_path)
        if book['file_path']:
            file_path = os.path.join('static', book['file_path'])
            if os.path.exists(file_path):
                os.remove(file_path)
        conn.execute("DELETE FROM books WHERE id = ?", (book_id,))
        conn.commit()
        flash("Книга удалена!", "success")
    else:
        flash("Книга не найдена!", "error")
    conn.close()
    return redirect(url_for('admin'))

# ===== Скачивание =====
@app.route('/download/<int:book_id>')
def download_book(book_id):
    conn = get_db_connection()
    book = conn.execute("""
        SELECT file_path, original_filename 
        FROM books 
        WHERE id = ?
    """, (book_id,)).fetchone()
    conn.close()

    if book and book['file_path']:
        server_path = book['file_path']  # например "uploads/e9a79ae7cf24435b89ccb6dc0102ec2a.pdf"
        orig_name = book['original_filename'] or "Без названия.pdf"

        return send_from_directory(
            directory='static',
            path=server_path,
            as_attachment=True,
            # Здесь указываем, под каким именем хотим, чтобы скачивался файл
            download_name=orig_name
        )
    else:
        return "Файл не найден", 404


# ===== Бэкап =====
@app.route('/backup', methods=['POST'])
def backup_db():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    backup_name = f"library_backup_{uuid.uuid4().hex}.db"
    backup_path = os.path.join(BACKUP_DIR, backup_name)
    shutil.copyfile(DATABASE, backup_path)
    flash(f"Резервная копия БД создана: {backup_name}", "success")
    return redirect(url_for('admin'))

if __name__ == '__main__':
    app.run(debug=True)