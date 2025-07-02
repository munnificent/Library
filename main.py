import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import json
import os
import shutil
import re
import random

# --- Константы ---
BOOKS_JSON_FILE = 'books.json'
ASSETS_ROOT = 'assets'
COVERS_DIR = os.path.join(ASSETS_ROOT, 'img')
FILES_DIR = os.path.join(ASSETS_ROOT, 'files')

class BookManagerApp(tk.Tk):
    """
    Графическое приложение для управления каталогом книг (books.json).
    """
    def __init__(self):
        super().__init__()
        self._setup_window()
        self._init_state()
        self._create_widgets()
        self._populate_initial_data()

    # --- 1. Инициализация и настройка ---

    def _setup_window(self):
        """Настраивает главное окно приложения."""
        self.title("Менеджер библиотеки")
        self.geometry("1000x700")
        self.resizable(True, True)

        # Стилизация виджетов
        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure('TFrame', background='#f0f0f0')
        style.configure('TLabel', background='#f0f0f0', font=('Arial', 11))
        style.configure('TButton', font=('Arial', 10), padding=5)
        style.configure('TEntry', font=('Arial', 11))
        style.configure('TCombobox', font=('Arial', 11))
        style.configure('Header.TLabel', font=('Arial', 12, 'bold'))

    def _init_state(self):
        """Инициализирует переменные состояния."""
        self.books_data = []
        self.edit_index = None  # Индекс редактируемой книги

        # Переменные для виджетов Tkinter
        self.direction_var = tk.StringVar()
        self.material_type_var = tk.StringVar()
        self.file_option_var = tk.StringVar(value="file")

    def _populate_initial_data(self):
        """Загружает начальные данные и обновляет UI."""
        os.makedirs(COVERS_DIR, exist_ok=True)
        os.makedirs(FILES_DIR, exist_ok=True)
        self.books_data = self._load_books()
        self._refresh_books_listbox()

    # --- 2. Создание интерфейса ---

    def _create_widgets(self):
        """Создает и размещает все виджеты в окне."""
        main_frame = ttk.Frame(self, padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Конфигурация сетки
        main_frame.columnconfigure(0, weight=1, minsize=300)
        main_frame.columnconfigure(1, weight=2, minsize=500)
        main_frame.rowconfigure(0, weight=1)

        # Левая колонка: список книг
        list_frame = self._create_list_frame(main_frame)
        list_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 15))

        # Правая колонка: форма для редактирования
        form_frame = self._create_form_frame(main_frame)
        form_frame.grid(row=0, column=1, sticky="nsew")

    def _create_list_frame(self, parent):
        """Создает фрейм со списком книг и кнопками управления."""
        frame = ttk.Frame(parent)
        frame.rowconfigure(1, weight=1)
        frame.columnconfigure(0, weight=1)

        ttk.Label(frame, text="Список книг", style='Header.TLabel').grid(row=0, column=0, sticky="w", pady=(0, 10))

        # Listbox и Scrollbar
        listbox_frame = ttk.Frame(frame)
        listbox_frame.grid(row=1, column=0, sticky="nsew")
        listbox_frame.rowconfigure(0, weight=1)
        listbox_frame.columnconfigure(0, weight=1)

        self.books_listbox = tk.Listbox(listbox_frame, font=('Arial', 11), selectbackground="#0078d7", selectforeground="white")
        self.books_listbox.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(listbox_frame, orient=tk.VERTICAL, command=self.books_listbox.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.books_listbox.config(yscrollcommand=scrollbar.set)

        # Кнопки под списком
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=2, column=0, sticky="ew", pady=(10, 0))

        edit_button = ttk.Button(btn_frame, text="Редактировать", command=self._edit_selected_book)
        edit_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 5))

        delete_button = ttk.Button(btn_frame, text="Удалить", command=self._delete_selected_book)
        delete_button.pack(side=tk.LEFT, expand=True, fill=tk.X)

        return frame

    def _create_form_frame(self, parent):
        """Создает фрейм с формой для ввода данных о книге."""
        frame = ttk.Frame(parent)
        frame.columnconfigure(1, weight=1)

        # --- Поля ввода ---
        fields = {
            "Название:": "title_entry", "Автор:": "author_entry", "Направление:": "direction_combobox",
            "Тип материала:": "material_type_combobox", "Год издания:": "year_entry", "Язык:": "language_entry"
        }
        # Валидация для поля "Год"
        validate_cmd = (self.register(self._validate_year), '%P')

        for i, (label, widget_name) in enumerate(fields.items()):
            ttk.Label(frame, text=label).grid(row=i, column=0, sticky="w", pady=5)
            if "combobox" in widget_name:
                values = ["Учебные материалы", "Научная литература", "Справочные издания", "Естественные науки",
                          "Технические науки", "Гуманитарные науки", "Социальные науки", "Экономические науки"] if "direction" in widget_name \
                         else ["Учебники", "Учебные пособия", "Практикумы", "Монографии", "Диссертации"]
                var = self.direction_var if "direction" in widget_name else self.material_type_var
                widget = ttk.Combobox(frame, textvariable=var, values=values, state="readonly")
            elif "year" in widget_name:
                widget = ttk.Entry(frame, validate='key', validatecommand=validate_cmd)
            else:
                widget = ttk.Entry(frame)
            widget.grid(row=i, column=1, sticky="ew", pady=2)
            setattr(self, widget_name, widget)

        # --- Описание (Text) ---
        ttk.Label(frame, text="Описание:").grid(row=6, column=0, sticky="nw", pady=5)
        self.description_text = tk.Text(frame, height=5, font=('Arial', 11), relief=tk.SOLID, borderwidth=1)
        self.description_text.grid(row=6, column=1, sticky="ew", pady=2)

        # --- Выбор файла/ссылки ---
        self._create_file_link_widgets(frame, 7)

        # --- Кнопки управления формой ---
        action_btn_frame = ttk.Frame(frame)
        action_btn_frame.grid(row=11, column=1, sticky="e", pady=(20, 0))

        self.add_or_save_button = ttk.Button(action_btn_frame, text="Добавить книгу", command=self._on_add_or_save)
        self.add_or_save_button.pack(side=tk.LEFT, padx=(0, 10))

        self.cancel_button = ttk.Button(action_btn_frame, text="Отменить", command=self._clear_form)
        # Кнопка "Отменить" будет показана только в режиме редактирования

        return frame

    def _create_file_link_widgets(self, parent, start_row):
        """Создает виджеты для выбора обложки, файла или ссылки."""
        # Обложка
        ttk.Label(parent, text="Обложка (файл):").grid(row=start_row, column=0, sticky="w", pady=5)
        cover_frame = self._create_browse_frame(parent, self._browse_cover)
        cover_frame.grid(row=start_row, column=1, sticky="ew")
        self.cover_path_entry = cover_frame.winfo_children()[0]

        # Переключатель Файл/Ссылка
        radio_frame = ttk.Frame(parent)
        radio_frame.grid(row=start_row + 1, column=0, columnspan=2, sticky="w", pady=5)
        ttk.Radiobutton(radio_frame, text="Файл книги", variable=self.file_option_var, value="file", command=self._toggle_file_link_fields).pack(side=tk.LEFT)
        ttk.Radiobutton(radio_frame, text="Ссылка (URL)", variable=self.file_option_var, value="cloud", command=self._toggle_file_link_fields).pack(side=tk.LEFT, padx=20)

        # Поле для файла книги
        self.file_label = ttk.Label(parent, text="Файл книги:")
        self.file_label.grid(row=start_row + 2, column=0, sticky="w", pady=5)
        self.file_frame = self._create_browse_frame(parent, self._browse_file)
        self.file_frame.grid(row=start_row + 2, column=1, sticky="ew")
        self.file_path_entry = self.file_frame.winfo_children()[0]

        # Поле для ссылки
        self.cloud_link_label = ttk.Label(parent, text="Ссылка (URL):")
        self.cloud_link_entry = ttk.Entry(parent)
        self._toggle_file_link_fields()

    def _create_browse_frame(self, parent, command):
        """Создает фрейм с полем ввода и кнопкой 'Обзор'."""
        frame = ttk.Frame(parent)
        entry = ttk.Entry(frame)
        entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 5))
        button = ttk.Button(frame, text="Обзор...", command=command)
        button.pack(side=tk.LEFT)
        return frame

    # --- 3. Логика обработки данных и событий ---

    def _on_add_or_save(self):
        """Обработчик нажатия кнопки 'Добавить'/'Сохранить'."""
        if self.edit_index is None:
            self._add_book()
        else:
            self._save_edited_book()

    def _add_book(self):
        """Добавляет новую книгу."""
        data = self._collect_form_data()
        if not data["title"]:
            messagebox.showwarning("Внимание", "Поле 'Название' обязательно для заполнения.")
            return

        new_id = self._get_next_id()
        data['id'] = new_id

        # Обработка файлов
        data['cover'] = self._copy_and_rename_asset(self.cover_path_entry.get(), COVERS_DIR, data, new_id)
        if self.file_option_var.get() == "file":
            data['fileLink'] = self._copy_and_rename_asset(self.file_path_entry.get(), FILES_DIR, data, new_id)

        self.books_data.append(data)
        self._save_books()
        self._refresh_books_listbox()
        self._clear_form()
        messagebox.showinfo("Успех", f"Книга '{data['title']}' успешно добавлена.")

    def _edit_selected_book(self):
        """Заполняет форму данными выбранной книги для редактирования."""
        selection = self.books_listbox.curselection()
        if not selection:
            messagebox.showwarning("Внимание", "Выберите книгу из списка для редактирования.")
            return
        
        self.edit_index = selection[0]
        book_data = self.books_data[self.edit_index]
        self._populate_form(book_data)

        # Обновляем UI для режима редактирования
        self.add_or_save_button.config(text="Сохранить")
        self.cancel_button.pack(side=tk.LEFT)

    def _save_edited_book(self):
        """Сохраняет изменения в редактируемой книге."""
        data = self._collect_form_data()
        if not data["title"]:
            messagebox.showwarning("Внимание", "Поле 'Название' не может быть пустым.")
            return

        book_id = self.books_data[self.edit_index]['id']
        data['id'] = book_id # ID не меняется

        # Обновляем пути к файлам, если они были изменены
        new_cover_path = self.cover_path_entry.get()
        if new_cover_path:
            self._delete_asset(self.books_data[self.edit_index].get('cover'))
            data['cover'] = self._copy_and_rename_asset(new_cover_path, COVERS_DIR, data, book_id)

        if self.file_option_var.get() == "file":
            self._delete_asset(self.books_data[self.edit_index].get('fileLink')) # Удаляем старый файл, если был
            data['cloudLink'] = ""
            new_file_path = self.file_path_entry.get()
            if new_file_path:
                data['fileLink'] = self._copy_and_rename_asset(new_file_path, FILES_DIR, data, book_id)
        else: # Выбрана ссылка
            self._delete_asset(self.books_data[self.edit_index].get('fileLink'))
            data['fileLink'] = ""

        self.books_data[self.edit_index].update(data)
        self._save_books()
        self._refresh_books_listbox()
        self._clear_form()
        messagebox.showinfo("Успех", f"Данные книги '{data['title']}' обновлены.")

    def _delete_selected_book(self):
        """Удаляет выбранную книгу и связанные с ней файлы."""
        selection = self.books_listbox.curselection()
        if not selection:
            messagebox.showwarning("Внимание", "Выберите книгу для удаления.")
            return

        index = selection[0]
        book = self.books_data[index]
        
        if messagebox.askyesno("Подтверждение", f"Вы уверены, что хотите удалить книгу '{book['title']}'?"):
            self._delete_asset(book.get('cover'))
            self._delete_asset(book.get('fileLink'))
            
            del self.books_data[index]
            self._save_books()
            self._refresh_books_listbox()
            self._clear_form() # Сбрасываем форму, если удалялась редактируемая книга
            messagebox.showinfo("Успех", "Книга удалена.")

    # --- 4. Вспомогательные функции и UI ---

    def _collect_form_data(self):
        """Собирает данные из полей формы в словарь."""
        return {
            "title": self.title_entry.get().strip(),
            "author": self.author_entry.get().strip(),
            "direction": self.direction_var.get(),
            "material_type": self.material_type_var.get(),
            "year": int(self.year_entry.get()) if self.year_entry.get().isdigit() else 0,
            "language": self.language_entry.get().strip(),
            "description": self.description_text.get("1.0", tk.END).strip(),
            "cover": "", "fileLink": "",
            "cloudLink": self.cloud_link_entry.get().strip() if self.file_option_var.get() == 'cloud' else ""
        }

    def _populate_form(self, book):
        """Заполняет поля формы данными из словаря book."""
        self._clear_form()
        self.title_entry.insert(0, book.get("title", ""))
        self.author_entry.insert(0, book.get("author", ""))
        self.direction_var.set(book.get("direction", ""))
        self.material_type_var.set(book.get("material_type", ""))
        self.year_entry.insert(0, str(book.get("year", "")))
        self.language_entry.insert(0, book.get("language", ""))
        self.description_text.insert("1.0", book.get("description", ""))

        if book.get("fileLink"):
            self.file_option_var.set("file")
        elif book.get("cloudLink"):
            self.file_option_var.set("cloud")
            self.cloud_link_entry.insert(0, book.get("cloudLink", ""))
        self._toggle_file_link_fields()

    def _clear_form(self):
        """Очищает все поля формы и сбрасывает режим редактирования."""
        self.title_entry.delete(0, tk.END)
        self.author_entry.delete(0, tk.END)
        self.year_entry.delete(0, tk.END)
        self.language_entry.delete(0, tk.END)
        self.cover_path_entry.delete(0, tk.END)
        self.file_path_entry.delete(0, tk.END)
        self.cloud_link_entry.delete(0, tk.END)
        self.description_text.delete("1.0", tk.END)
        self.direction_var.set("")
        self.material_type_var.set("")
        
        self.edit_index = None
        self.add_or_save_button.config(text="Добавить книгу")
        self.cancel_button.pack_forget()

    def _refresh_books_listbox(self):
        """Обновляет список книг в Listbox."""
        self.books_listbox.delete(0, tk.END)
        for book in self.books_data:
            display_text = f"{book['id']}: {book['title']} ({book.get('author', 'N/A')})"
            self.books_listbox.insert(tk.END, display_text)

    def _toggle_file_link_fields(self):
        """Переключает видимость полей для файла и ссылки."""
        is_file = self.file_option_var.get() == "file"
        if is_file:
            self.file_label.grid()
            self.file_frame.grid()
            self.cloud_link_label.grid_remove()
            self.cloud_link_entry.grid_remove()
        else:
            self.file_label.grid_remove()
            self.file_frame.grid_remove()
            self.cloud_link_label.grid(row=9, column=0, sticky="w", pady=5)
            self.cloud_link_entry.grid(row=9, column=1, sticky="ew")

    # --- 5. Работа с файлами и JSON ---

    def _load_books(self):
        """Загружает книги из JSON-файла."""
        if not os.path.exists(BOOKS_JSON_FILE):
            return []
        try:
            with open(BOOKS_JSON_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            messagebox.showerror("Ошибка чтения", f"Файл {BOOKS_JSON_FILE} повреждён. Будет создан новый файл при сохранении.")
            return []

    def _save_books(self):
        """Сохраняет текущий список книг в JSON."""
        with open(BOOKS_JSON_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.books_data, f, ensure_ascii=False, indent=2)

    def _browse_file(self):
        path = filedialog.askopenfilename(filetypes=[("PDF файлы", "*.pdf"), ("Все файлы", "*.*")])
        if path:
            self.file_path_entry.delete(0, tk.END)
            self.file_path_entry.insert(0, path)

    def _browse_cover(self):
        path = filedialog.askopenfilename(filetypes=[("Изображения", "*.jpg *.jpeg *.png"), ("Все файлы", "*.*")])
        if path:
            self.cover_path_entry.delete(0, tk.END)
            self.cover_path_entry.insert(0, path)

    def _copy_and_rename_asset(self, src_path, dest_dir, book_data, book_id):
        """Копирует и переименовывает файл обложки или книги."""
        if not src_path or not os.path.isfile(src_path):
            return ""
        
        # Очистка имени от недопустимых символов
        author = re.sub(r'[\\/*?:"<>|]', "", book_data.get('author', 'NoAuthor'))
        title = re.sub(r'[\\/*?:"<>|]', "", book_data.get('title', 'NoTitle'))[:50]
        _, ext = os.path.splitext(src_path)
        
        new_filename = f"{author.replace(' ', '_')}_{title.replace(' ', '_')}_{book_id}_{random.randint(1000, 9999)}{ext}"
        dest_path = os.path.join(dest_dir, new_filename)

        try:
            shutil.copy2(src_path, dest_path)
            return dest_path.replace("\\", "/")
        except Exception as e:
            messagebox.showerror("Ошибка копирования", f"Не удалось скопировать файл: {e}")
            return ""

    def _delete_asset(self, file_path):
        """Безопасно удаляет файл, если он существует."""
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except OSError as e:
                messagebox.showerror("Ошибка удаления", f"Не удалось удалить файл {file_path}: {e}")

    def _get_next_id(self):
        """Возвращает следующий уникальный ID."""
        if not self.books_data:
            return 1
        return max(book.get('id', 0) for book in self.books_data) + 1

    def _validate_year(self, P):
        """Проверяет, является ли вводимое значение числом."""
        return str.isdigit(P) or P == ""

if __name__ == "__main__":
    app = BookManagerApp()
    app.mainloop()