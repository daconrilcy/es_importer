import { initDarkMode } from "darkmode";
import { initChunkedTablePagination } from "./chunk_table.js";
import { attachMenuEventListeners, setActiveMenuItemFromPath } from "menu";
import { initRadioGroups } from "radio-group";
import { initHorizontalScroll } from "./scroll-horizontal.js";
import { initModifyTitle } from "./modify-title.js";
import { initBtnListFile } from "./btn-list-file.js";
import { InitMappingPreview } from "./mapping/mapping.js";
import {initCsvHeaderOptions} from "./csv-headers-options.js";

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
    initBtnListFile(urlDemandee);
    attachMenuEventListeners();
    setActiveMenuItemFromPath(urlDemandee);

    // Initialisation pagination si table présente (chargement initial)
    initChunkedTablePagination();
    initCsvHeaderOptions();

    // Initialisation des events mappings
    InitMappingPreview();

    // Initialisation spécifique Dropzone pour la page d’upload
    if (urlDemandee === '/upload') {
        import('../dropzone-init.js').then(mod => {
            requestAnimationFrame(() => {
                mod.initializeDropzone();
            });
        });
    }
}
