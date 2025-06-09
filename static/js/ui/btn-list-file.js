import { initChunkedTablePagination } from "./chunk_table.js";
import { initHorizontalScroll } from "./scroll-horizontal.js";

/**
 * Initialise les boutons de la liste de fichiers (visualiser et supprimer).
 * À appeler après injection du HTML contenant #file-one-list.
 */
export function initBtnListFile() {
    const fileListContainer = document.getElementById('file-one-list');
    if (!fileListContainer) return;

    // Évite de ré-attacher plusieurs fois les événements
    if (fileListContainer.dataset.listenersAttached === 'true') return;

    fileListContainer.addEventListener('click', async function (event) {
        const visualizeBtn = event.target.closest('.btn-visualize');
        const deleteBtn = event.target.closest('.btn-delete');

        // Visualiser un fichier
        if (visualizeBtn && fileListContainer.contains(visualizeBtn)) {
            event.preventDefault();
            const fileId = visualizeBtn.dataset.fileId;
            if (!fileId) return;

            try {
                const response = await fetch(`/file/preview/data-zone/${fileId}/0`, {
                    headers: { 'X-Requested-With': 'XMLHttpRequest' }
                });

                if (!response.ok) throw new Error('Erreur serveur');

                const html = await response.text();
                injectPreview(html, visualizeBtn);
                history.pushState(null, '', `/file/preview/${fileId}/`);
                toggleClassActive(visualizeBtn, fileListContainer);

            } catch (e) {
                alert('Erreur lors du chargement de la prévisualisation du fichier.');
                console.error(e);
            }
        }

        // Supprimer un fichier
        if (deleteBtn && fileListContainer.contains(deleteBtn)) {
            event.preventDefault();
            const fileId = deleteBtn.dataset.fileId;
            console.log(`Suppression demandée pour le fichier ID : ${fileId}`);
            // 👉 future intégration backend ici
        }
    });

    fileListContainer.dataset.listenersAttached = 'true';
}

/**
 * Injecte la prévisualisation dans #datas-zone et initialise la pagination.
 * @param {string} html - Le HTML retourné par l’API
 * @param {HTMLElement} visualizeBtn - Le bouton cliqué
 */
function injectPreview(html, visualizeBtn) {
    const datasZone = document.getElementById('datas-zone');
    if (!datasZone) return;

    datasZone.innerHTML = html;

    // Mise à jour de l’input associé
    const fileFrontNameInput = document.getElementById('file_front_name');
    if (fileFrontNameInput) {
        const text = visualizeBtn.textContent.trim();
        const fileId = visualizeBtn.dataset.fileId;

        fileFrontNameInput.value = text;
        fileFrontNameInput.dataset.originalValue = text;
        fileFrontNameInput.dataset.fileId = fileId;
    }

    // Initialisation de la pagination dynamique du tableau
    initChunkedTablePagination();
    // Initialisation du scroll horizontal
    initHorizontalScroll();
}

function toggleClassActive(active_btn, btn_container) {
    if (!active_btn) return;
    if (!btn_container) return;
    let btn_list = btn_container.querySelectorAll('.btn-visualize');
    btn_list.forEach(button => {
        button.classList.remove('active');
    });
    active_btn.classList.add('active');
}
