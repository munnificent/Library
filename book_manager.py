import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import json
import os
import shutil
import random

# Название JSON-файла, где хранятся данные о книгах
BOOKS_JSON_FILE = 'books.json'

# Папки, в которые будут копироваться файлы
COVERS_DIR = 'assets/img'    # для обложек
FILES_DIR = 'assets/files'   # для локальных файлов книг

class BookManager(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Book Manager")

        # Разрешаем свободное изменение размеров окна
        self.resizable(True, True)

        # Можно задать исходный (стартовый) размер окна
        self.geometry("900x600")

        # Создаём необходимые папки (если не существуют)
        os.makedirs(COVERS_DIR, exist_ok=True)
        os.makedirs(FILES_DIR, exist_ok=True)

        # Настраиваем стили ttk
        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure('TFrame', background='#f0f0f0')
        style.configure('TLabel', background='#f0f0f0', font=('Arial', 11))
        style.configure('TButton', font=('Arial', 11))
        style.configure('TEntry', font=('Arial', 11))

        # Загружаем имеющиеся книги
        self.books_data = self.load_books()

        # --- Поле для хранения индекса редактируемой книги (None = добавляем новую) ---
        self.edit_index = None

        # --- Основной контейнер (Frame) ---
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Настраиваем grid для плавного масштабирования
        main_frame.columnconfigure(0, weight=0)  # для списка (листбокс)
        main_frame.columnconfigure(1, weight=1)  # для формы
        main_frame.rowconfigure(0, weight=1)

        # --------- Левая часть: список книг + кнопки "Редактировать" / "Удалить" ---------
        list_frame = ttk.Frame(main_frame)
        list_frame.grid(row=0, column=0, rowspan=10, padx=(0, 20), sticky="ns")

        ttk.Label(list_frame, text="Список книг:", font=('Arial', 12, 'bold')).pack(anchor="w")

        self.books_listbox = tk.Listbox(list_frame, width=40, font=('Arial', 11))
        self.books_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.books_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.books_listbox.config(yscrollcommand=scrollbar.set)

        # Фрейм для кнопок
        btn_frame = ttk.Frame(list_frame)
        btn_frame.pack(pady=5, anchor="e")

        edit_button = ttk.Button(btn_frame, text="Редактировать", command=self.edit_selected_book)
        edit_button.pack(side=tk.LEFT, padx=5)

        delete_button = ttk.Button(btn_frame, text="Удалить", command=self.delete_selected_book)
        delete_button.pack(side=tk.LEFT, padx=5)

        # --------- Правая часть: форма для добавления/редактирования книги ---------
        form_frame = ttk.Frame(main_frame)
        form_frame.grid(row=0, column=1, sticky="nsew")

        # Текст о том, что ID формируется автоматически
        ttk.Label(form_frame, text="(ID присваивается автоматически при добавлении)").grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 10)
        )

        # Поле: title
        ttk.Label(form_frame, text="Название:").grid(row=1, column=0, sticky="w", pady=5)
        self.title_entry = ttk.Entry(form_frame, width=40)
        self.title_entry.grid(row=1, column=1, sticky="ew")

        # Поле: author
        ttk.Label(form_frame, text="Автор:").grid(row=2, column=0, sticky="w", pady=5)
        self.author_entry = ttk.Entry(form_frame, width=40)
        self.author_entry.grid(row=2, column=1, sticky="ew")

        # --- Выпадающий список (Combobox) для direction ---
        ttk.Label(form_frame, text="Направление:").grid(row=3, column=0, sticky="w", pady=5)
        self.direction_var = tk.StringVar()
        self.direction_combobox = ttk.Combobox(
            form_frame,
            textvariable=self.direction_var,
            values=[
                "Учебные материалы",
                "Научная литература",
                "Справочные издания",
                "Естественные науки",
                "Технические науки",
                "Гуманитарные науки",
                "Социальные науки",
                "Экономические науки"
            ],
            state="readonly",  # если хотим запретить ввод произвольного текста
            width=38
        )
        self.direction_combobox.grid(row=3, column=1, sticky="ew")

        # --- Выпадающий список (Combobox) для material_type ---
        ttk.Label(form_frame, text="Тип материала:").grid(row=4, column=0, sticky="w", pady=5)
        self.material_type_var = tk.StringVar()
        self.material_type_combobox = ttk.Combobox(
            form_frame,
            textvariable=self.material_type_var,
            values=[
                "Учебники",
                "Учебные пособия",
                "Практикумы",
                "Монографии",
                "Диссертации"
            ],
            state="readonly",  # или можно убрать, чтобы пользователь мог вводить свой вариант
            width=38
        )
        self.material_type_combobox.grid(row=4, column=1, sticky="ew")

        # Поле: год
        ttk.Label(form_frame, text="Год издания:").grid(row=5, column=0, sticky="w", pady=5)
        self.year_entry = ttk.Entry(form_frame, width=40)
        self.year_entry.grid(row=5, column=1, sticky="ew")

        # Поле: язык
        ttk.Label(form_frame, text="Язык:").grid(row=6, column=0, sticky="w", pady=5)
        self.language_entry = ttk.Entry(form_frame, width=40)
        self.language_entry.grid(row=6, column=1, sticky="ew")

        # Поле: описание (Text)
        ttk.Label(form_frame, text="Описание:").grid(row=7, column=0, sticky="nw", pady=5)
        self.description_text = tk.Text(form_frame, width=30, height=4, font=('Arial', 11))
        self.description_text.grid(row=7, column=1, sticky="ew")

        # Поле: обложка (cover)
        ttk.Label(form_frame, text="Обложка (файл):").grid(row=8, column=0, sticky="w", pady=5)
        cover_frame = ttk.Frame(form_frame)
        cover_frame.grid(row=8, column=1, sticky="w")

        self.cover_path_entry = ttk.Entry(cover_frame, width=27)
        self.cover_path_entry.pack(side=tk.LEFT, padx=(0, 5))

        cover_browse_button = ttk.Button(cover_frame, text="Обзор", command=self.browse_cover)
        cover_browse_button.pack(side=tk.LEFT)

        # Радио-кнопки: "Локальный файл" или "Ссылка на облако"
        self.file_option_var = tk.StringVar(value="file")  # по умолчанию "file"

        radio_frame = ttk.Frame(form_frame)
        radio_frame.grid(row=9, column=0, columnspan=2, sticky="w", pady=5)

        ttk.Label(radio_frame, text="Выберите формат книги: ").pack(side=tk.LEFT)

        file_radiobutton = ttk.Radiobutton(
            radio_frame, text="Файл", variable=self.file_option_var, value="file",
            command=self.toggle_file_link_fields
        )
        file_radiobutton.pack(side=tk.LEFT, padx=5)

        link_radiobutton = ttk.Radiobutton(
            radio_frame, text="Ссылка (облако)", variable=self.file_option_var, value="cloud",
            command=self.toggle_file_link_fields
        )
        link_radiobutton.pack(side=tk.LEFT, padx=5)

        # Поле: локальный файл
        ttk.Label(form_frame, text="Файл книги:").grid(row=10, column=0, sticky="w", pady=5)
        file_frame = ttk.Frame(form_frame)
        file_frame.grid(row=10, column=1, sticky="w")

        self.file_path_entry = ttk.Entry(file_frame, width=27)
        self.file_path_entry.pack(side=tk.LEFT, padx=(0, 5))

        self.file_browse_button = ttk.Button(file_frame, text="Обзор", command=self.browse_file)
        self.file_browse_button.pack(side=tk.LEFT)

        # Поле: облачная ссылка
        ttk.Label(form_frame, text="Ссылка (cloudLink):").grid(row=11, column=0, sticky="w", pady=5)
        self.cloud_link_entry = ttk.Entry(form_frame, width=40)
        self.cloud_link_entry.grid(row=11, column=1, sticky="ew")

        # Кнопка (по умолчанию "Добавить книгу", при редактировании - "Сохранить изменения")
        self.add_or_save_button = ttk.Button(form_frame, text="Добавить книгу", command=self.on_add_or_save)
        self.add_or_save_button.grid(row=12, column=1, pady=10, sticky="e")

        # Кнопка "Выход"
        exit_button = ttk.Button(form_frame, text="Выход", command=self.quit)
        exit_button.grid(row=13, column=1, pady=5, sticky="e")

        # Настраиваем расширение колонок/строк (чтобы при растягивании окна элементы заполняли пространство)
        for i in range(14):
            form_frame.rowconfigure(i, weight=0)
        form_frame.columnconfigure(1, weight=1)

        # Изначально, если выбран "file", поле облачной ссылки отключим
        self.toggle_file_link_fields()

        # Подключаем поддержку Ctrl+V для всех Entry и Text
        self.enable_ctrl_v(self.title_entry)
        self.enable_ctrl_v(self.author_entry)
        self.enable_ctrl_v(self.direction_combobox)
        self.enable_ctrl_v(self.material_type_combobox)
        self.enable_ctrl_v(self.year_entry)
        self.enable_ctrl_v(self.language_entry)
        self.enable_ctrl_v(self.cover_path_entry)
        self.enable_ctrl_v(self.file_path_entry)
        self.enable_ctrl_v(self.cloud_link_entry)
        self.enable_ctrl_v_text(self.description_text)

        # Отобразим уже имеющиеся книги в листбоксе
        self.refresh_books_listbox()

    # ----------------------------------------------------------------
    # Вспомогательные методы
    # ----------------------------------------------------------------

    def load_books(self):
        """Загрузить книги из JSON или вернуть пустой список."""
        if os.path.exists(BOOKS_JSON_FILE):
            try:
                with open(BOOKS_JSON_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, ValueError):
                messagebox.showerror("Ошибка JSON", "Файл books.json повреждён. Он будет перезаписан.")
                return []
        else:
            return []

    def save_books(self):
        """Сохранить список книг в JSON."""
        with open(BOOKS_JSON_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.books_data, f, ensure_ascii=False, indent=2)

    def refresh_books_listbox(self):
        """Обновить содержимое списка (Listbox) книг."""
        self.books_listbox.delete(0, tk.END)
        for idx, book in enumerate(self.books_data):
            display_text = f"{idx+1}. {book['title']} — {book['author']}"
            self.books_listbox.insert(tk.END, display_text)

    def toggle_file_link_fields(self):
        """Включает/выключает поля для файла или ссылки в зависимости от выбора."""
        if self.file_option_var.get() == "file":
            self.file_path_entry.configure(state="normal")
            self.file_browse_button.configure(state="normal")
            self.cloud_link_entry.configure(state="disabled")
        else:
            self.file_path_entry.configure(state="disabled")
            self.file_browse_button.configure(state="disabled")
            self.cloud_link_entry.configure(state="normal")

    # ----------------------------------------------------------------
    # Поддержка Ctrl+V для Entry и Text
    # ----------------------------------------------------------------

    def enable_ctrl_v(self, widget):
        """
        Включить поддержку Ctrl+V для отдельного ttk.Entry или ttk.Combobox.
        По умолчанию на Windows обычно работает, но в некоторых окружениях — нет.
        """
        def paste_handler(event):
            widget.event_generate("<<Paste>>")
            return "break"

        # Для combobox (или entry) используем эту привязку
        widget.bind("<Control-v>", paste_handler)

    def enable_ctrl_v_text(self, text_widget):
        """
        Включить поддержку Ctrl+V для tk.Text.
        """
        def paste_handler(event):
            text_widget.event_generate("<<Paste>>")
            return "break"

        text_widget.bind("<Control-v>", paste_handler)

    # ----------------------------------------------------------------
    # Методы для копирования с переименованием
    # ----------------------------------------------------------------

    def rename_and_copy_file(self, source_path, destination_dir, author, title, file_id):
        """
        Копирует файл source_path в папку destination_dir,
        переименовывая в формате:
          Автор_Название_ID_СлучайноеЧисло.расширение

        Возвращает новый относительный путь (str) или "" при ошибке.
        """
        if not source_path or not os.path.isfile(source_path):
            return ""

        author_sanitized = author.replace(" ", "_")
        title_sanitized  = title.replace(" ", "_")
        random_part = random.randint(1000, 9999)
        _, ext = os.path.splitext(source_path)

        new_filename = f"{author_sanitized}_{title_sanitized}_{file_id}_{random_part}{ext}"
        new_full_path = os.path.join(destination_dir, new_filename)

        try:
            shutil.copy2(source_path, new_full_path)
            return new_full_path.replace("\\", "/")  # для Windows
        except Exception as e:
            messagebox.showerror("Ошибка копирования файла", str(e))
            return ""

    # ----------------------------------------------------------------
    # Кнопка "Добавить книгу" или "Сохранить изменения"
    # ----------------------------------------------------------------

    def on_add_or_save(self):
        """
        Если self.edit_index is None, значит мы создаём новую книгу.
        Иначе - сохраняем изменения в существующую.
        """
        if self.edit_index is None:
            self.add_book()
        else:
            self.save_edited_book()

    # ----------------------------------------------------------------
    # Добавление новой книги
    # ----------------------------------------------------------------

    def add_book(self):
        """Создать новую книгу, скопировать файлы, сохранить в JSON."""
        title, author, direction, material_type, year, language, description = self.collect_form_data()

        if not title:
            messagebox.showwarning("Предупреждение", "Введите название книги!")
            return

        new_id = len(self.books_data) + 1
        file_choice = self.file_option_var.get()
        file_path_input = self.file_path_entry.get().strip()
        cloud_link_input = self.cloud_link_entry.get().strip()
        cover_path_input = self.cover_path_entry.get().strip()

        new_book = {
            "id": new_id,
            "title": title,
            "author": author,
            "direction": direction,
            "material_type": material_type,
            "year": year,
            "language": language,
            "description": description,
            "cover": "",
            "fileLink": "",
            "cloudLink": ""
        }

        # Копирование обложки
        if cover_path_input:
            new_cover = self.rename_and_copy_file(
                cover_path_input, COVERS_DIR, author, title, new_id
            )
            new_book["cover"] = new_cover

        # Локальный файл или ссылка
        if file_choice == "file" and file_path_input:
            new_file_link = self.rename_and_copy_file(
                file_path_input, FILES_DIR, author, title, new_id
            )
            new_book["fileLink"] = new_file_link
        elif file_choice == "cloud":
            new_book["cloudLink"] = cloud_link_input

        self.books_data.append(new_book)
        self.save_books()
        self.refresh_books_listbox()

        messagebox.showinfo("Успех", f"Книга '{title}' успешно добавлена!")
        self.clear_form()

    # ----------------------------------------------------------------
    # Редактирование существующей книги
    # ----------------------------------------------------------------

    def edit_selected_book(self):
        """
        Пользователь нажал "Редактировать": берём выбранную книгу,
        заполняем форму, запоминаем индекс книги.
        """
        selection = self.books_listbox.curselection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите книгу для редактирования!")
            return

        index = selection[0]
        self.edit_index = index
        book = self.books_data[index]

        # Заполняем форму существующими данными
        self.title_entry.delete(0, tk.END)
        self.title_entry.insert(0, book.get("title", ""))

        self.author_entry.delete(0, tk.END)
        self.author_entry.insert(0, book.get("author", ""))

        # Заполняем combobox (direction)
        self.direction_var.set(book.get("direction", ""))

        # Заполняем combobox (material_type)
        self.material_type_var.set(book.get("material_type", ""))

        self.year_entry.delete(0, tk.END)
        self.year_entry.insert(0, book.get("year", ""))

        self.language_entry.delete(0, tk.END)
        self.language_entry.insert(0, book.get("language", ""))

        self.description_text.delete("1.0", tk.END)
        self.description_text.insert(tk.END, book.get("description", ""))

        # Обложку и файл/ссылку очистим (user при желании выберет новые)
        self.cover_path_entry.delete(0, tk.END)

        file_link = book.get("fileLink", "")
        cloud_link = book.get("cloudLink", "")

        if file_link:
            self.file_option_var.set("file")
            self.file_path_entry.configure(state="normal")
            self.file_browse_button.configure(state="normal")
            self.cloud_link_entry.configure(state="disabled")
            self.file_path_entry.delete(0, tk.END)
            # Не подставляем старый путь, т.к. пользователь может выбирать новый
            self.cloud_link_entry.delete(0, tk.END)
        elif cloud_link:
            self.file_option_var.set("cloud")
            self.file_path_entry.configure(state="disabled")
            self.file_browse_button.configure(state="disabled")
            self.cloud_link_entry.configure(state="normal")
            self.cloud_link_entry.delete(0, tk.END)
            self.cloud_link_entry.insert(0, cloud_link)
        else:
            # Ни fileLink, ни cloudLink
            self.file_option_var.set("file")
            self.file_path_entry.delete(0, tk.END)
            self.cloud_link_entry.delete(0, tk.END)

        # Меняем текст кнопки на "Сохранить изменения"
        self.add_or_save_button.config(text="Сохранить изменения")

    def save_edited_book(self):
        """
        Сохранить изменения в уже существующую книгу.
        Удаляем старые файлы (обложка, файл книги), если пользователь выбрал новые.
        При переходе с "файла" на "ссылку" (или наоборот) удаляем старый файл.
        """
        index = self.edit_index
        if index is None:
            return  # на всякий случай

        # Получаем данные из формы
        title, author, direction, material_type, year, language, description = self.collect_form_data()
        file_choice = self.file_option_var.get()
        cover_path_input = self.cover_path_entry.get().strip()
        file_path_input = self.file_path_entry.get().strip()
        cloud_link_input = self.cloud_link_entry.get().strip()

        if not title:
            messagebox.showwarning("Предупреждение", "Введите название книги!")
            return

        # Текущая книга
        book = self.books_data[index]
        old_cover = book.get("cover", "")
        old_file_link = book.get("fileLink", "")
        old_cloud_link = book.get("cloudLink", "")
        old_id = book["id"]  # ID не меняем

        # Обновляем поля
        book["title"] = title
        book["author"] = author
        book["direction"] = direction
        book["material_type"] = material_type
        book["year"] = year
        book["language"] = language
        book["description"] = description

        # --- Обложка ---
        if cover_path_input:
            # Если выбрана новая обложка => удаляем старую
            if old_cover and os.path.exists(old_cover):
                try:
                    os.remove(old_cover)
                except Exception as e:
                    messagebox.showerror("Ошибка удаления старой обложки", str(e))

            new_cover = self.rename_and_copy_file(
                cover_path_input, COVERS_DIR, author, title, old_id
            )
            book["cover"] = new_cover
        else:
            # Не трогаем старую обложку
            pass

        # --- Файл / Ссылка ---
        if file_choice == "file":
            # Переходим на локальный файл
            if file_path_input:
                # Если раньше был fileLink, удаляем старый файл
                if old_file_link and os.path.exists(old_file_link):
                    try:
                        os.remove(old_file_link)
                    except Exception as e:
                        messagebox.showerror("Ошибка удаления старого файла", str(e))

                # Если раньше была ссылка (cloudLink) - обнулим
                if old_cloud_link:
                    book["cloudLink"] = ""

                new_file_link = self.rename_and_copy_file(
                    file_path_input, FILES_DIR, author, title, old_id
                )
                book["fileLink"] = new_file_link
            else:
                # Если не указали новый файл, оставляем старый fileLink (если был),
                # но обнулим cloudLink (если был)
                if old_cloud_link:
                    book["cloudLink"] = ""
        else:
            # Переходим на cloudLink
            if old_file_link and os.path.exists(old_file_link):
                # Удаляем старый локальный файл
                try:
                    os.remove(old_file_link)
                except Exception as e:
                    messagebox.showerror("Ошибка удаления старого файла", str(e))
                book["fileLink"] = ""

            book["cloudLink"] = cloud_link_input

        # Сохраняем изменения
        self.save_books()
        self.refresh_books_listbox()
        messagebox.showinfo("Успех", f"Изменения для книги '{title}' сохранены!")

        # Выходим из режима редактирования
        self.edit_index = None
        self.clear_form()

    def collect_form_data(self):
        """Собрать данные из формы (общие поля). Возвращает tuple."""
        title = self.title_entry.get().strip()
        author = self.author_entry.get().strip()
        direction = self.direction_var.get().strip()  # берём из Combobox
        material_type = self.material_type_var.get().strip()
        year = self.year_entry.get().strip()
        language = self.language_entry.get().strip()
        description = self.description_text.get("1.0", tk.END).strip()
        return title, author, direction, material_type, year, language, description

    # ----------------------------------------------------------------
    # Методы для выбора файлов
    # ----------------------------------------------------------------

    def browse_cover(self):
        """Открыть диалог для выбора файла обложки."""
        file_path = filedialog.askopenfilename(
            title="Выберите файл обложки",
            filetypes=[("Изображения", "*.jpg *.jpeg *.png *.gif"), ("Все файлы", "*.*")]
        )
        if file_path:
            self.cover_path_entry.delete(0, tk.END)
            self.cover_path_entry.insert(0, file_path)

    def browse_file(self):
        """Открыть диалог для выбора файла книги."""
        file_path = filedialog.askopenfilename(
            title="Выберите файл книги (PDF и т.п.)",
            filetypes=[("PDF файлы", "*.pdf"), ("Все файлы", "*.*")]
        )
        if file_path:
            self.file_path_entry.delete(0, tk.END)
            self.file_path_entry.insert(0, file_path)

    # ----------------------------------------------------------------
    # Удаление книги
    # ----------------------------------------------------------------

    def delete_selected_book(self):
        """
        Удалить выбранную книгу из списка и из JSON.
        Также удаляем локальные файлы (обложку и файл книги),
        если они существуют на диске.
        """
        selection = self.books_listbox.curselection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите книгу для удаления!")
            return

        index = selection[0]
        book_to_delete = self.books_data[index]
        title = book_to_delete.get('title', 'NoTitle')

        cover_path = book_to_delete.get("cover", "")
        if cover_path and os.path.exists(cover_path):
            try:
                os.remove(cover_path)
            except Exception as e:
                messagebox.showerror("Ошибка удаления обложки", str(e))

        file_link = book_to_delete.get("fileLink", "")
        if file_link and os.path.exists(file_link):
            try:
                os.remove(file_link)
            except Exception as e:
                messagebox.showerror("Ошибка удаления файла книги", str(e))

        # Удаляем книгу из общего списка
        del self.books_data[index]
        self.save_books()
        self.refresh_books_listbox()

        messagebox.showinfo("Успех", f"Книга '{title}' успешно удалена!")
        # Если мы были в режиме редактирования именно этой книги — сбрасываем
        if self.edit_index == index:
            self.edit_index = None
            self.clear_form()

    # ----------------------------------------------------------------
    # Очистка формы
    # ----------------------------------------------------------------

    def clear_form(self):
        """Очистить поля формы, сбросить edit_index и вернуть кнопку в режим 'Добавить'."""
        self.edit_index = None
        self.title_entry.delete(0, tk.END)
        self.author_entry.delete(0, tk.END)
        self.direction_var.set("")
        self.material_type_var.set("")
        self.year_entry.delete(0, tk.END)
        self.language_entry.delete(0, tk.END)
        self.description_text.delete("1.0", tk.END)
        self.cover_path_entry.delete(0, tk.END)
        self.file_path_entry.delete(0, tk.END)
        self.cloud_link_entry.delete(0, tk.END)
        self.file_option_var.set("file")
        self.toggle_file_link_fields()
        self.add_or_save_button.config(text="Добавить книгу")

def main():
    app = BookManager()
    app.mainloop()

if __name__ == "__main__":
    main()
