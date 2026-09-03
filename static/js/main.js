/**
 * FLIPKART STOREFRONT UI INTERACTIONS & HELPERS
 */

document.addEventListener('DOMContentLoaded', () => {
  // Search bar handling
  const searchForm = document.getElementById('fkSearchForm');
  const searchInput = document.getElementById('fkSearchInput');
  
  if (searchForm && searchInput) {
    searchForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const q = searchInput.value.trim();
      if (q) {
        window.location.href = `/products?q=${encodeURIComponent(q)}`;
      }
    });
  }

  // Auto-dismiss alerts after 5 seconds
  document.querySelectorAll('.fk-alert').forEach(alertEl => {
    setTimeout(() => {
      alertEl.style.transition = 'opacity 0.5s ease';
      alertEl.style.opacity = '0';
      setTimeout(() => alertEl.remove(), 500);
    }, 5000);
  });

  // User Dropdown hover / click handling
  const userMenuBtn = document.getElementById('fkUserMenuBtn');
  const userDropdown = document.getElementById('fkUserDropdown');
  if (userMenuBtn && userDropdown) {
    userMenuBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      userDropdown.classList.toggle('show');
    });

    document.addEventListener('click', () => {
      userDropdown.classList.remove('show');
    });
  }
});
