document.addEventListener('DOMContentLoaded', () => {
  const bookListEl = document.getElementById('book-list');
  const paginationEl = document.getElementById('pagination');

  // Фильтры
  const directionFilter = document.getElementById('direction-filter');
  const typeFilter = document.getElementById('type-filter');
  const yearFilter = document.getElementById('year-filter');
  const langFilter = document.getElementById('lang-filter');
  const searchTitle = document.getElementById('search-title');
  const resetBtn = document.getElementById('reset-filters');

  // Пагинация
  let currentPage = 1;
  const booksPerPage = 20;

  let allBooks = [];
  let filteredBooks = [];

  // 1. Загрузка books.json (async/await)
  async function fetchBooks() {
    try {
      const resp = await fetch('books.json');
      if (!resp.ok) {
        throw new Error(`Ошибка сети: статус ${resp.status}`);
      }
      const data = await resp.json();
      allBooks = data;
      filteredBooks = [...allBooks]; // по умолчанию отображаем все
      renderPage();
    } catch (err) {
      console.error("Ошибка при загрузке books.json:", err);
      bookListEl.innerHTML = "<p style='color:red;'>Не удалось загрузить книги.</p>";
    }
  }

  fetchBooks();

  // 2. Рендер текущей страницы
  function renderPage() {
    const startIndex = (currentPage - 1) * booksPerPage;
    const endIndex = startIndex + booksPerPage;
    const pageBooks = filteredBooks.slice(startIndex, endIndex);

    renderBooks(pageBooks);
    renderPagination();
  }

  // 3. Функция отрисовки карточек (с DocumentFragment для оптимизации)
  function renderBooks(books) {
    bookListEl.innerHTML = '';
    const fragment = document.createDocumentFragment();

    books.forEach(book => {
      const col = document.createElement('div');
      col.className = "col s12 m6";

      const card = document.createElement('div');
      card.className = "card hoverable";
      card.style.cursor = 'pointer';

      // Сохраняем data-* (если нужно для дополнительного функционала)
      card.dataset.direction = book.direction.toLowerCase();
      card.dataset.type = book.material_type.toLowerCase();
      card.dataset.year = book.year;
      card.dataset.lang = book.language.toLowerCase();

      // Обработчик клика (открытие модалки)
      card.addEventListener('click', () => showModal(book));

      // card-image
      const cardImage = document.createElement('div');
      cardImage.className = "card-image";

      const coverImg = document.createElement('img');
      coverImg.className = "book-cover";
      coverImg.src = book.cover || "https://placehold.co/600x900/EEE/31343C?font=lato&text=обложка\nСКОРО";
      cardImage.appendChild(coverImg);

      // card-content
      const cardContent = document.createElement('div');
      cardContent.className = "card-content";
      cardContent.style.color = "#000";

      const titleSpan = document.createElement('span');
      titleSpan.className = "card-title";
      titleSpan.style.color = "#0019ff";
      titleSpan.textContent = book.title;

      const pAuthor = document.createElement('p');
      pAuthor.textContent = "Автор: " + book.author;

      const pYear = document.createElement('p');
      pYear.textContent = "Год: " + book.year;

      const pLang = document.createElement('p');
      pLang.textContent = "Язык: " + book.language;

      const pCat = document.createElement('p');
      pCat.style.color = "#777";
      pCat.style.fontSize = "14px";
      pCat.textContent = book.direction + " / " + book.material_type;

      // Сборка карточки
      cardContent.appendChild(titleSpan);
      cardContent.appendChild(pAuthor);
      cardContent.appendChild(pYear);
      cardContent.appendChild(pLang);
      cardContent.appendChild(pCat);

      card.appendChild(cardImage);
      card.appendChild(cardContent);
      col.appendChild(card);

      fragment.appendChild(col);
    });

    // Единовременное добавление в DOM
    bookListEl.appendChild(fragment);
  }

  // 4. Модалка "Подробнее"
  function showModal(book) {
    document.getElementById('modal-cover').src = book.cover || "";
    document.getElementById('modal-title').textContent = book.title;
    document.getElementById('modal-author').textContent = "Автор: " + book.author;
    document.getElementById('modal-year').textContent = "Год: " + book.year;
    document.getElementById('modal-lang').textContent = "Язык: " + book.language;
    document.getElementById('modal-description').textContent = book.description || "";
    document.getElementById('modal-category').textContent = book.direction + " / " + book.material_type;

    // Кнопки скачивания
    const dlButtons = document.getElementById('download-buttons');
    dlButtons.innerHTML = '';

    // fileLink (локально)
    if (book.fileLink) {
      const localBtn = document.createElement('a');
      localBtn.className = "btn waves-effect waves-light";
      localBtn.style.marginRight = "10px";
      localBtn.style.backgroundColor = "#FFC700";
      localBtn.style.color = "#000";
      localBtn.textContent = "Скачать (локально)";
      localBtn.href = book.fileLink;
      localBtn.setAttribute('download', book.fileLink.split('/').pop());
      dlButtons.appendChild(localBtn);
    }

    // cloudLink (облачно)
    if (book.cloudLink) {
      const cloudBtn = document.createElement('a');
      cloudBtn.className = "btn waves-effect waves-light";
      cloudBtn.style.backgroundColor = "#FFC700";
      cloudBtn.style.color = "#000";
      cloudBtn.textContent = "Скачать (облако)";
      cloudBtn.href = book.cloudLink;
      dlButtons.appendChild(cloudBtn);
    }

    // Открываем модалку
    const modalEl = document.getElementById('modal-overlay');
    const instance = M.Modal.getInstance(modalEl);
    instance.open();
  }

  // 5. Пагинация (с DocumentFragment для оптимизации)
  function renderPagination() {
    paginationEl.innerHTML = '';
    const totalPages = Math.ceil(filteredBooks.length / booksPerPage);

    if (totalPages <= 1) return;

    const fragment = document.createDocumentFragment();

    for (let i = 1; i <= totalPages; i++) {
      const pageLink = document.createElement('button');
      pageLink.className = "btn-small waves-effect";
      pageLink.style.marginRight = "5px";
      pageLink.textContent = i;

      if (i === currentPage) {
        pageLink.style.backgroundColor = "#FFC700";
        pageLink.style.color = "#000";
      } else {
        pageLink.style.backgroundColor = "#0019ff";
        pageLink.style.color = "#fff";
      }

      pageLink.addEventListener('click', () => {
        currentPage = i;
        renderPage();
      });

      fragment.appendChild(pageLink);
    }

    paginationEl.appendChild(fragment);
  }

  // 6. Фильтрация
  function applyFilters() {
    const dirVal = directionFilter.value.trim().toLowerCase();
    const typeVal = typeFilter.value.trim().toLowerCase();
    const yearVal = yearFilter.value.trim();
    const langVal = langFilter.value.trim().toLowerCase();
    const searchVal = searchTitle.value.trim().toLowerCase();

    filteredBooks = allBooks.filter(book => {
      const matchDirection = !dirVal || book.direction.toLowerCase().includes(dirVal);
      const matchType = !typeVal || book.material_type.toLowerCase().includes(typeVal);
      const matchYear = !yearVal || String(book.year) === yearVal;
      const matchLang = !langVal || book.language.toLowerCase() === langVal;
      const matchTitle = !searchVal || book.title.toLowerCase().includes(searchVal);
      return matchDirection && matchType && matchYear && matchLang && matchTitle;
    });

    currentPage = 1;
    renderPage();
  }

  // Сброс фильтров
  resetBtn.addEventListener('click', () => {
    directionFilter.value = "";
    typeFilter.value = "";
    yearFilter.value = "";
    langFilter.value = "";
    searchTitle.value = "";
    filteredBooks = [...allBooks];
    currentPage = 1;
    renderPage();
  });

  // Привязка обработчиков к фильтрам
  directionFilter.addEventListener('change', applyFilters);
  typeFilter.addEventListener('change', applyFilters);
  yearFilter.addEventListener('input', applyFilters);
  langFilter.addEventListener('change', applyFilters);
  searchTitle.addEventListener('input', applyFilters);
});
