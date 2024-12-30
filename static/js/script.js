document.addEventListener('DOMContentLoaded', () => {
  // Теперь мы используем data-id, чтобы корректно формировать /download/<id>
  const bookItems = document.querySelectorAll('.book-item');
  bookItems.forEach(card => {
    card.addEventListener('click', () => {
      const bookId = card.dataset.id || '';
      const coverEl = card.querySelector('.book-cover');
      const coverSrc = coverEl ? coverEl.getAttribute('src') : '';

      const titleEl = card.querySelector('.card-title');
      const title = titleEl ? titleEl.innerText : '';

      const author = card.querySelector('p:nth-of-type(1)')?.innerText || '';
      const year = card.querySelector('p:nth-of-type(2)')?.innerText || '';
      const lang = card.querySelector('p:nth-of-type(3)')?.innerText || '';
      const desc = card.dataset.description || '';

      // Заполняем модалку
      document.getElementById('modal-cover').src = coverSrc;
      document.getElementById('modal-title').textContent = title;
      document.getElementById('modal-author').textContent = author;
      document.getElementById('modal-year').textContent = year;
      document.getElementById('modal-lang').textContent = lang;
      document.getElementById('modal-description').textContent = desc;

      // Формируем ссылку для скачивания
      const downloadLink = document.getElementById('download-link');
      if (bookId) {
        downloadLink.href = `/download/${bookId}`;
      } else {
        downloadLink.href = '#'; 
      }

      // Открываем модалку Materialize
      const modalEl = document.getElementById('modal-overlay');
      const instance = M.Modal.getInstance(modalEl);
      instance.open();
    });
  });

  // Фильтры + Поиск
  const directionFilter = document.getElementById('direction-filter');
  const typeFilter = document.getElementById('type-filter');
  const yearFilter = document.getElementById('year-filter');
  const langFilter = document.getElementById('lang-filter');
  const searchTitle = document.getElementById('search-title');
  const resetBtn = document.getElementById('reset-filters');
  const bookList = document.getElementById('book-list');

  function applyFilters() {
    const dirVal = directionFilter.value.trim().toLowerCase();
    const typeVal = typeFilter.value.trim().toLowerCase();
    const yearVal = yearFilter.value.trim();
    const langVal = langFilter.value.trim().toLowerCase();
    const searchVal = searchTitle.value.trim().toLowerCase();

    const books = bookList.querySelectorAll('.book-item');
    books.forEach(book => {
      const bookDir = book.dataset.direction || '';
      const bookType = book.dataset.type || '';
      const bookYear = book.dataset.year || '';
      const bookLang = book.dataset.lang || '';
      const cardTitle = book.querySelector('.card-title')?.innerText.toLowerCase() || '';

      let show = true;

      if (dirVal && !bookDir.includes(dirVal)) show = false;
      if (typeVal && !bookType.includes(typeVal)) show = false;
      if (yearVal && bookYear !== yearVal) show = false;
      if (langVal && bookLang !== langVal) show = false;

      if (searchVal && !cardTitle.includes(searchVal)) {
        show = false;
      }

      book.style.display = show ? '' : 'none';
    });
  }

  resetBtn.addEventListener('click', () => {
    directionFilter.value = "";
    typeFilter.value = "";
    yearFilter.value = "";
    langFilter.value = "";
    searchTitle.value = "";
    applyFilters();
  });

  directionFilter.addEventListener('change', applyFilters);
  typeFilter.addEventListener('change', applyFilters);
  yearFilter.addEventListener('input', applyFilters);
  langFilter.addEventListener('change', applyFilters);
  searchTitle.addEventListener('input', applyFilters);
});
