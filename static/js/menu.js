/**
 * Gère les interactions du menu (hamburger, fermeture mobile, etc.)
 * À appeler dynamiquement après un injectContent()
 */
export function attachMenuEventListeners() {
    const menu = document.querySelector('.menu');
    const menuToggle = document.querySelector('.menu-toggle');

    // Ferme le menu burger après clic sur un lien
    document.querySelectorAll('.menu-item').forEach(item => {
        item.addEventListener('click', () => {
            if (menu && menu.classList.contains('open')) {
                menu.classList.remove('open');
                if (menuToggle) {
                    menuToggle.classList.remove('open');
                    menuToggle.setAttribute('aria-expanded', 'false');
                }
            }
        });
    });

    // Active ou désactive le menu burger
    if (menuToggle && menu) {
        menuToggle.setAttribute('aria-expanded', 'false');
        menuToggle.setAttribute('aria-label', 'Ouvrir ou fermer le menu');
        menuToggle.setAttribute('role', 'button');

        menuToggle.addEventListener('click', () => {
            const isOpen = menu.classList.toggle('open');
            menuToggle.classList.toggle('open', isOpen);
            menuToggle.setAttribute('aria-expanded', isOpen.toString());
        });
    }
}

/**
 * Met à jour la classe active du menu selon l’URL
 * @param {string} pathname - l’URL (par défaut l’URL courante)
 */
export function setActiveMenuItemFromPath(pathname = window.location.pathname) {
    let route = '';
    if (pathname === '/upload') route = 'upload';
    else if (pathname === '/import/mappings') route = 'mappings';
    else if (pathname === '/import/importers') route = 'importers';
    else if (pathname === '/import/processors') route = 'processors';
    else if (pathname === '/file/list-all') route = 'file-list-all';

    document.querySelectorAll('.menu-item').forEach(item => {
        item.classList.remove('active');
        if (item.dataset.route === route) {
            item.classList.add('active');
        }
    });
}
