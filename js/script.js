// =================================
//  Инициализация приложения
// =================================
document.addEventListener('DOMContentLoaded', init);

function init() {
    setupEventListeners();
    fetchBooks();
    initializeModals();
    registerServiceWorker();
}

// =================================
//  Глобальное состояние (State)
// =================================
let allBooks = [];
let filteredBooks = [];
let currentPage = 1;
const booksPerPage = 20;

// =================================
//  DOM-элементы
// =================================
const DOM = {
    bookList: document.getElementById('book-list'),
    pagination: document.getElementById('pagination'),
    filters: {
        direction: document.getElementById('direction-filter'),
        type: document.getElementById('type-filter'),
        year: document.getElementById('year-filter'),
        lang: document.getElementById('lang-filter'),
        search: document.getElementById('search-title'),
    },
    resetBtn: document.getElementById('reset-filters'),
    modal: {
        instance: null, // Инициализируется в initializeModals
        element: document.getElementById('modal-book-details'),
        cover: document.getElementById('modal-cover'),
        title: document.getElementById('modal-title'),
        author: document.getElementById('modal-author'),
        year: document.getElementById('modal-year'),
        lang: document.getElementById('modal-lang'),
        description: document.getElementById('modal-description'),
        category: document.getElementById('modal-category'),
        downloadButtons: document.getElementById('download-buttons'),
    }
};

// =================================
//  Основные функции
// =================================

/**
 * Загружает данные о книгах из JSON-файла
 */
/**
 * Загружает данные о книгах из JSON-файла
 */
async function fetchBooks() {
  try {
      // Убедитесь, что здесь именно 'books.json'
      const response = await fetch('books.json'); 
      if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
      }
      allBooks = await response.json();
      filteredBooks = [...allBooks];
      render(); // Первичная отрисовка
  } catch (error) {
      console.error("Ошибка при загрузке книг:", error);
      DOM.bookList.innerHTML = `<p class="center-align red-text">Не удалось загрузить каталог книг. Пожалуйста, попробуйте обновить страницу.</p>`;
  }
}

/**
 * Применяет фильтры и обновляет отображение
 */
function applyFilters() {
    const filters = {
        direction: DOM.filters.direction.value.trim().toLowerCase(),
        type: DOM.filters.type.value.trim().toLowerCase(),
        year: DOM.filters.year.value.trim(),
        lang: DOM.filters.lang.value.trim().toLowerCase(),
        search: DOM.filters.search.value.trim().toLowerCase(),
    };

    filteredBooks = allBooks.filter(book => {
        const matchDirection = !filters.direction || book.direction.toLowerCase().includes(filters.direction);
        const matchType = !filters.type || book.material_type.toLowerCase().includes(filters.type);
        const matchYear = !filters.year || String(book.year) === filters.year;
        const matchLang = !filters.lang || book.language.toLowerCase() === filters.lang;
        const matchTitle = !filters.search || book.title.toLowerCase().includes(filters.search);
        return matchDirection && matchType && matchYear && matchLang && matchTitle;
    });

    currentPage = 1;
    render();
}

/**
 * Сбрасывает все фильтры к значениям по умолчанию
 */
function resetFilters() {
    for (let key in DOM.filters) {
        DOM.filters[key].value = '';
    }
    filteredBooks = [...allBooks];
    currentPage = 1;
    render();
}

// =================================
//  Функции отрисовки (Render)
// =================================

/**
 * Главная функция отрисовки, вызывающая дочерние
 */
function render() {
    renderBooks();
    renderPagination();
}

/**
 * Отрисовывает карточки книг на текущей странице
 */
function renderBooks() {
    const startIndex = (currentPage - 1) * booksPerPage;
    const endIndex = startIndex + booksPerPage;
    const pageBooks = filteredBooks.slice(startIndex, endIndex);

    if (pageBooks.length === 0) {
        DOM.bookList.innerHTML = `<p class="center-align grey-text">Книги по вашему запросу не найдены.</p>`;
        return;
    }
    
    // Использование шаблонных строк для создания HTML
    DOM.bookList.innerHTML = pageBooks.map(book => `
        <div class="col s12 m6 l4">
            <div class="card hoverable book-card" data-book-id="${book.id}">
                <div class="card-image">
                    <img src="${book.cover || 'assets/img/placeholder.png'}" alt="Обложка книги ${book.title}" class="book-cover">
                    <span class="card-title">${book.title}</span>
                </div>
                <div class="card-content">
                    <p><strong>Автор:</strong> ${book.author}</p>
                    <p><strong>Год:</strong> ${book.year}</p>
                </div>
            </div>
        </div>
    `).join('');
}

/**
 * Отрисовывает элементы пагинации
 */
function renderPagination() {
    const totalPages = Math.ceil(filteredBooks.length / booksPerPage);
    DOM.pagination.innerHTML = '';

    if (totalPages <= 1) return;

    let paginationHTML = '';
    for (let i = 1; i <= totalPages; i++) {
        const activeClass = (i === currentPage) ? 'brand-bg-yellow black-text' : 'brand-bg-blue white-text';
        paginationHTML += `<button class="btn-small waves-effect ${activeClass}" data-page="${i}">${i}</button>`;
    }
    DOM.pagination.innerHTML = paginationHTML;
}


/**
 * Показывает модальное окно с деталями о книге
 * @param {string} bookId - ID книги для отображения
 */
function showModal(bookId) {
  const book = allBooks.find(b => String(b.id) === String(bookId));
  if (!book) return;

  DOM.modal.cover.src = book.cover || 'assets/img/placeholder.png';
  DOM.modal.title.textContent = book.title;
  DOM.modal.author.textContent = `Автор: ${book.author}`;
  DOM.modal.year.textContent = `Год: ${book.year}`;
  DOM.modal.lang.textContent = `Язык: ${book.language}`;
  DOM.modal.description.textContent = book.description || 'Описание отсутствует.';
  DOM.modal.category.textContent = `${book.direction} / ${book.material_type}`;

  // --- ИСПРАВЛЕННАЯ ЛОГИКА ГЕНЕРАЦИИ КНОПОК ---
  DOM.modal.downloadButtons.innerHTML = ''; // Очищаем контейнер

  // 1. Проверяем наличие локального файла
  if (book.fileLink) {
      DOM.modal.downloadButtons.innerHTML += `
          <a href="${book.fileLink}" class="btn waves-effect waves-light brand-bg-yellow black-text" download>
              Скачать (файл)
          </a>`;
  }
  
  // 2. Проверяем наличие облачной ссылки
  if (book.cloudLink) {
      DOM.modal.downloadButtons.innerHTML += `
          <a href="${book.cloudLink}" target="_blank" rel="noopener" class="btn waves-effect waves-light brand-bg-blue white-text" style="margin-left: 10px;">
              Открыть (облако)
          </a>`;
  }
  // --- КОНЕЦ ИСПРАВЛЕНИЯ ---

  DOM.modal.instance.open();
}

// =================================
//  Настройка обработчиков событий
// =================================
function setupEventListeners() {
    Object.values(DOM.filters).forEach(filter => {
        filter.addEventListener('input', applyFilters);
        filter.addEventListener('change', applyFilters);
    });

    DOM.resetBtn.addEventListener('click', resetFilters);

    // Делегирование событий для кликов по карточкам
    DOM.bookList.addEventListener('click', (event) => {
        const card = event.target.closest('.book-card');
        if (card && card.dataset.bookId) {
            showModal(card.dataset.bookId);
        }
    });

    // Делегирование событий для пагинации
    DOM.pagination.addEventListener('click', (event) => {
        if (event.target.tagName === 'BUTTON' && event.target.dataset.page) {
            currentPage = Number(event.target.dataset.page);
            render();
            window.scrollTo(0, 0); // Прокрутка вверх при смене страницы
        }
    });
}

// =================================
//  Сервисные функции (PWA, Modals)
// =================================

/**
 * Инициализирует модальные окна Materialize
 */
function initializeModals() {
    const modalElements = document.querySelectorAll('.modal');
    M.Modal.init(modalElements);
    DOM.modal.instance = M.Modal.getInstance(DOM.modal.element);
}

/**
 * Регистрирует Service Worker для PWA
 */
function registerServiceWorker() {
    if ('serviceWorker' in navigator) {
        window.addEventListener('load', () => {
            navigator.serviceWorker.register('/sw.js')
                .then(registration => console.log('ServiceWorker registration successful:', registration.scope))
                .catch(err => console.log('ServiceWorker registration failed:', err));
        });
    }
}