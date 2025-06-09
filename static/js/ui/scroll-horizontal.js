export function initHorizontalScroll() {
    const container = document.querySelector('.csv-container');
    const wrapper = document.querySelector('.csv-table-wrapper');
    const leftBtn = document.querySelector('.scroll-lateral-button.left');
    const rightBtn = document.querySelector('.scroll-lateral-button.right');

    if (!container || !wrapper || !leftBtn || !rightBtn) return;

    leftBtn.onclick = () => { wrapper.scrollBy({ left: -200, behavior: 'smooth' }); };
    rightBtn.onclick = () => { wrapper.scrollBy({ left: 200, behavior: 'smooth' }); };
} 