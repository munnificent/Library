document.addEventListener('DOMContentLoaded', () => {
  const directionFilter = document.getElementById('direction-filter');
  const typeFilter = document.getElementById('type-filter');
  const yearFilter = document.getElementById('year-filter');
  const langFilter = document.getElementById('lang-filter');

  const resetBtn = document.getElementById('reset-filters');
  const bookList = document.getElementById('book-list');

  // Модальное окно
  const modalOverlay = document.getElementById('modal-overlay');
  const modalClose = document.getElementById('modal-close');
  const modalCover = document.getElementById('modal-cover');
  const modalTitle = document.getElementById('modal-title');
  const modalAuthor = document.getElementById('modal-author');
  const modalYear = document.getElementById('modal-year');
  const modalLang = document.getElementById('modal-lang');
  const modalDescription = document.getElementById('modal-description');
  const downloadLink = document.getElementById('download-link');

  function applyFilters() {
    const dirVal = directionFilter.value.trim().toLowerCase();
    const typeVal = typeFilter.value.trim().toLowerCase();
    const yearVal = yearFilter.value.trim();
    const langVal = langFilter.value.trim().toLowerCase();

    const books = bookList.querySelectorAll('.book-item');
    books.forEach(book => {
      const bookDir = book.dataset.direction;
      const bookType = book.dataset.type;
      const bookYear = book.dataset.year;
      const bookLang = book.dataset.lang;

      let show = true;
      if (dirVal && bookDir !== dirVal) show = false;
      if (typeVal && bookType !== typeVal) show = false;
      if (yearVal && bookYear !== yearVal) show = false;
      if (langVal && bookLang !== langVal) show = false;

      book.style.display = show ? 'flex' : 'none';
    });
  }

  // Сброс
  resetBtn.addEventListener('click', () => {
    directionFilter.value = "";
    typeFilter.value = "";
    yearFilter.value = "";
    langFilter.value = "";
    applyFilters();
  });

  directionFilter.addEventListener('change', applyFilters);
  typeFilter.addEventListener('change', applyFilters);
  yearFilter.addEventListener('input', applyFilters);
  langFilter.addEventListener('change', applyFilters);

  // Кнопки "Подробнее"
  const detailButtons = document.querySelectorAll('.details-btn');
  detailButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      const bookItem = btn.closest('.book-item');
      if (!bookItem) return;

      const bookId = btn.dataset.id; 
      const coverSrc = bookItem.querySelector('.book-cover')?.getAttribute('src') || '';
      const title = bookItem.querySelector('h3')?.innerText || '';
      const authorLine = bookItem.querySelector('p:nth-of-type(1)')?.innerText || '';
      const yearLine = bookItem.querySelector('p:nth-of-type(2)')?.innerText || '';
      const langLine = bookItem.querySelector('p:nth-of-type(3)')?.innerText || '';

      // Предположим, мы храним описание в data-атрибуте
      const description = bookItem.dataset.description || '';

      modalCover.src = coverSrc;
      modalTitle.textContent = title;
      modalAuthor.textContent = authorLine;
      modalYear.textContent = yearLine;
      modalLang.textContent = langLine;
      modalDescription.textContent = description;

      // Ссылка на скачивание
      downloadLink.href = `/download/${bookId}`;

      // Показать модалку
      modalOverlay.style.display = 'flex';
    });
  });

  modalClose.addEventListener('click', () => {
    modalOverlay.style.display = 'none';
  });
  modalOverlay.addEventListener('click', (e) => {
    if (e.target === modalOverlay) {
      modalOverlay.style.display = 'none';
    }
  });
});



const description = bookItem.dataset.description || '';
modalDescription.textContent = description;

