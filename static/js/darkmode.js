export function initDarkMode() {
    const darkToggle = document.getElementById('darkToggle');
    if (!darkToggle) return; // Si le toggle n'est pas présent, on ne fait rien

    function applyDarkMode(mode) {
        if (mode === 'dark') {
            document.documentElement.classList.add('dark-mode');
            darkToggle.checked = true;
        } else {
            document.documentElement.classList.remove('dark-mode');
            darkToggle.checked = false;
        }
    }

    // Appliquer le thème au chargement
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
        applyDarkMode(savedTheme);
    } else {
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        applyDarkMode(prefersDark ? 'dark' : 'light');
    }

    // Nettoyer les anciens listeners pour éviter les doublons
    const newToggle = darkToggle.cloneNode(true);
    darkToggle.parentNode.replaceChild(newToggle, darkToggle);
    newToggle.addEventListener('change', () => {
        const newMode = newToggle.checked ? 'dark' : 'light';
        applyDarkMode(newMode);
        localStorage.setItem('theme', newMode);
    });
}