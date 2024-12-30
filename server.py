import os
import sqlite3
import uuid
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


# ===== Подключение к БД =====
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# ===== Инициализация БД =====
def init_db():
    if not os.path.exists(DATABASE):
        conn = get_db_connection()
        # Таблица "books" без поля "availability", а с "description"
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
            file_path TEXT
        );''')
        conn.commit()
        conn.close()
        print("Создана новая база данных library.db")

    # Создадим папку uploads в static, если её нет
    os.makedirs(os.path.join('static', 'uploads'), exist_ok=True)


init_db()


# ===== Главная страница (каталог) =====
@app.route('/')
def index():
    conn = get_db_connection()
    books = conn.execute("SELECT * FROM books").fetchall()
    conn.close()
    return render_template('index.html', books=books)


# ===== Логин =====
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


# ===== Логаут =====
@app.route('/logout')
def logout():
    session['logged_in'] = False
    flash("Вы вышли из админ-панели.", "info")
    return redirect(url_for('index'))


# ===== Админ-панель =====
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if not session.get('logged_in'):
        flash("Требуется вход в систему!", "error")
        return redirect(url_for('login'))

    if request.method == 'POST':
        # Считываем данные из формы
        title = request.form.get('title')
        author = request.form.get('author')
        direction = request.form.get('direction')
        material_type = request.form.get('material_type')
        year = request.form.get('year') or None
        language = request.form.get('language')
        description = request.form.get('description') or ''

        # Файлы
        cover_file = request.files.get('cover_file')
        download_file = request.files.get('download_file')

        cover_filename = None
        download_filename = None

        # Если загрузили обложку
        if cover_file and cover_file.filename.strip():
            basefilename = secure_filename(cover_file.filename)
            ext = os.path.splitext(basefilename)[1]
            unique_name = f"{uuid.uuid4().hex}{ext}"
            cover_filename = f"uploads/{unique_name}"
            cover_file.save(os.path.join('static', 'uploads', unique_name))

        # Если загрузили файл для скачивания
        if download_file and download_file.filename.strip():
            basefilename2 = secure_filename(download_file.filename)
            ext2 = os.path.splitext(basefilename2)[1]
            unique_name2 = f"{uuid.uuid4().hex}{ext2}"
            download_filename = f"uploads/{unique_name2}"
            download_file.save(os.path.join('static', 'uploads', unique_name2))

        if not title or not author:
            flash("Поля 'Название книги' и 'Автор' обязательны!", "error")
            return redirect(url_for('admin'))

        # Запись в БД
        conn = get_db_connection()
        conn.execute("""
            INSERT INTO books
            (title, author, direction, material_type, year, language, description, image_path, file_path)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (title, author, direction, material_type, year, language, description,
              cover_filename, download_filename))
        conn.commit()
        conn.close()

        flash("Книга успешно добавлена!", "success")
        return redirect(url_for('admin'))

    # GET-запрос
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
        # Удаляем файлы (по желанию)
        if book['image_path']:
            img_path = os.path.join('static', book['image_path'])
            if os.path.exists(img_path):
                os.remove(img_path)
        if book['file_path']:
            file_path = os.path.join('static', book['file_path'])
            if os.path.exists(file_path):
                os.remove(file_path)

        # Удаляем запись из БД
        conn.execute("DELETE FROM books WHERE id = ?", (book_id,))
        conn.commit()
        flash("Книга удалена!", "success")
    else:
        flash("Книга не найдена!", "error")
    conn.close()
    return redirect(url_for('admin'))


# ===== Скачивание файла =====
@app.route('/download/<int:book_id>')
def download_book(book_id):
    conn = get_db_connection()
    book = conn.execute("SELECT file_path FROM books WHERE id=?", (book_id,)).fetchone()
    conn.close()

    if book and book['file_path']:
        path_in_static = book['file_path']
        return send_from_directory(directory='static', path=path_in_static, as_attachment=True)
    else:
        return "Файл не найден", 404


if __name__ == '__main__':
    app.run(debug=True)
