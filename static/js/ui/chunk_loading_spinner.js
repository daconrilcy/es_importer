export function showLoadingSpinner(table) {
  let spinner = document.getElementById('chunk-loading-spinner');
  const tbody = table.querySelector('tbody');
  if (tbody) {
    tbody.classList.add('blur');
  }
  if (!spinner) {
    spinner = document.createElement('div');
    spinner.id = 'chunk-loading-spinner';
    spinner.className = 'chunk-loading-spinner-overlay';
    spinner.innerHTML = `
        <div class="chunk-loading-spinner-content">
          <div class="chunk-loading-spinner"></div>
          <div class="chunk-loading-spinner-text">Chargement...</div>
        </div>`;
    const container = table.closest('.csv-container') || table.parentElement;
   
    container.appendChild(spinner);
  } else {
    spinner.style.display = 'flex';
  }
}

export function hideLoadingSpinner() {
  const spinner = document.getElementById('chunk-loading-spinner');
  if (spinner) {
    spinner.style.display = 'none';
  }
  const table = document.querySelector('.csv-table');
  if (table) {
    const tbody = table.querySelector('tbody');
    if (tbody) {
      tbody.classList.remove('blur');
    }
  }
} 