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

  // 1. Загрузить books.json
  fetch('books.json')
    .then(resp => resp.json())
    .then(data => {
      allBooks = data;
      filteredBooks = allBooks; // по умолчанию всё
      renderPage();
    })
    .catch(err => {
      console.error("Ошибка при загрузке books.json:", err);
      bookListEl.innerHTML = "<p style='color:red;'>Не удалось загрузить книги.</p>";
    });

  // 2. Рендер текущей страницы
  function renderPage() {
    // Фильтруем + отображаем только нужную страницу
    const startIndex = (currentPage - 1) * booksPerPage;
    const endIndex = startIndex + booksPerPage;
    const pageBooks = filteredBooks.slice(startIndex, endIndex);

    renderBooks(pageBooks);
    renderPagination();
  }

  // 3. Функция отрисовки карточек
  function renderBooks(books) {
    bookListEl.innerHTML = '';
    books.forEach(book => {
      const col = document.createElement('div');
      col.className = "col s12 m6";

      const card = document.createElement('div');
      card.className = "card hoverable";
      card.style.cursor = 'pointer';

      // Сохраняем data-* для фильтра, не так уж нужно, но можно
      card.dataset.direction = book.direction.toLowerCase();
      card.dataset.type = book.material_type.toLowerCase();
      card.dataset.year = book.year;
      card.dataset.lang = book.language.toLowerCase();

      card.addEventListener('click', () => showModal(book));

      // card-image
      const cardImage = document.createElement('div');
      cardImage.className = "card-image";
      const coverImg = document.createElement('img');
      coverImg.className = "book-cover";
      coverImg.src = book.cover || "https://via.placeholder.com/400x250?text=No+Cover";
      cardImage.appendChild(coverImg);
      card.appendChild(cardImage);

      // card-content
      const cardContent = document.createElement('div');
      cardContent.className = "card-content";
      cardContent.style.color = "#000";

      const titleSpan = document.createElement('span');
      titleSpan.className = "card-title";
      titleSpan.style.color = "#0019ff";
      titleSpan.textContent = book.title;
      cardContent.appendChild(titleSpan);

      const pAuthor = document.createElement('p');
      pAuthor.textContent = "Автор: " + book.author;
      cardContent.appendChild(pAuthor);

      const pYear = document.createElement('p');
      pYear.textContent = "Год: " + book.year;
      cardContent.appendChild(pYear);

      const pLang = document.createElement('p');
      pLang.textContent = "Язык: " + book.language;
      cardContent.appendChild(pLang);

      const pCat = document.createElement('p');
      pCat.style.color = "#777";
      pCat.style.fontSize = "14px";
      pCat.textContent = book.direction + " / " + book.material_type;
      cardContent.appendChild(pCat);

      card.appendChild(cardContent);
      col.appendChild(card);
      bookListEl.appendChild(col);
    });
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
    dlButtons.innerHTML = ''; // очищаем

    // fileLink (локальный)
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

    // cloudLink (облачный)
    if (book.cloudLink) {
      const cloudBtn = document.createElement('a');
      cloudBtn.className = "btn waves-effect waves-light";
      cloudBtn.style.backgroundColor = "#FFC700";
      cloudBtn.style.color = "#000";
      cloudBtn.textContent = "Скачать (облако)";
      cloudBtn.href = book.cloudLink;
      dlButtons.appendChild(cloudBtn);
    }

    const modalEl = document.getElementById('modal-overlay');
    const instance = M.Modal.getInstance(modalEl);
    instance.open();
  }

  // 5. Пагинация
  function renderPagination() {
    paginationEl.innerHTML = '';
    const totalPages = Math.ceil(filteredBooks.length / booksPerPage);

    // Если всего 1 страница, скрываем пагинацию
    if (totalPages <= 1) return;

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

      paginationEl.appendChild(pageLink);
    }
  }

  // 6. Фильтрация
  function applyFilters() {
    const dirVal = directionFilter.value.trim().toLowerCase();
    const typeVal = typeFilter.value.trim().toLowerCase();
    const yearVal = yearFilter.value.trim();
    const langVal = langFilter.value.trim().toLowerCase();
    const searchVal = searchTitle.value.trim().toLowerCase();

    filteredBooks = allBooks.filter(book => {
      if (dirVal && !book.direction.toLowerCase().includes(dirVal)) return false;
      if (typeVal && !book.material_type.toLowerCase().includes(typeVal)) return false;
      if (yearVal && String(book.year) !== yearVal) return false;
      if (langVal && book.language.toLowerCase() !== langVal) return false;
      if (searchVal && !book.title.toLowerCase().includes(searchVal)) return false;
      return true;
    });

    currentPage = 1; // reset to first page
    renderPage();
  }

  resetBtn.addEventListener('click', () => {
    directionFilter.value = "";
    typeFilter.value = "";
    yearFilter.value = "";
    langFilter.value = "";
    searchTitle.value = "";
    filteredBooks = allBooks;
    currentPage = 1;
    renderPage();
  });

  directionFilter.addEventListener('change', applyFilters);
  typeFilter.addEventListener('change', applyFilters);
  yearFilter.addEventListener('input', applyFilters);
  langFilter.addEventListener('change', applyFilters);
  searchTitle.addEventListener('input', applyFilters);
});
