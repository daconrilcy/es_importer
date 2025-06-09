import { initDarkMode } from "darkmode";
import { initChunkedTablePagination } from "./chunk_table.js";
import { attachMenuEventListeners, setActiveMenuItemFromPath } from "menu";
import { initRadioGroups } from "radio-group";
import { initHorizontalScroll } from "./scroll-horizontal.js";
import { initModifyTitle } from "./modify-title.js";
import { initBtnListFile } from "./btn-list-file.js";

let observer = null;

/**
 * Injecte du contenu HTML dans #content et relance tous les scripts nécessaires.
 * @param {string} html - Le HTML à injecter
 * @param {string} urlDemandee - L’URL cible (utile pour la gestion de menu)
 */
export function injectContent(html, urlDemandee = window.location.pathname) {
    const content = document.getElementById('content');
    if (!content) return;

    // Injection du nouveau contenu
    content.innerHTML = html;

    // Réinitialisation des composants de page
    initDarkMode();
    initRadioGroups();
    initModifyTitle();
    initHorizontalScroll();
    initBtnListFile();
    attachMenuEventListeners();
    setActiveMenuItemFromPath(urlDemandee);

    // Initialisation pagination si table présente (chargement initial)
    initChunkedTablePagination();

    // Mise en place de l'observateur pour réinjection dynamique
    observeDatasZoneReplacement();

    // Initialisation spécifique Dropzone pour la page d’upload
    if (urlDemandee === '/upload') {
        import('../dropzone-init.js').then(mod => {
            requestAnimationFrame(() => {
                mod.initializeDropzone();
            });
        });
    }
}

/**
 * Observe les modifications dans #content et relance la pagination
 * uniquement si un tableau paginé est réinjecté.
 */
function observeDatasZoneReplacement() {
    const content = document.getElementById('content');
    if (!content) return;

    if (observer) observer.disconnect(); // évite les doublons

    observer = new MutationObserver(() => {
        requestAnimationFrame(() => {
            const csvTable = document.getElementById('csv-table');
            if (csvTable) {
                console.log('[DEBUG] #csv-table détecté → relance pagination');
                initChunkedTablePagination();
                initCsvHeaderOptions();

            }
        });
    });

    observer.observe(content, {
        childList: true,
        subtree: true
    });
}
