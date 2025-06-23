import { initChunkedTablePagination } from "./chunk_table.js";
import { InitMappingPreview } from "./mapping/mapping.js";
import { initHorizontalScroll } from "./scroll-horizontal.js";
import {queryDeleteFile} from "./../loader/file_deleter.js";
import {isIdInUrl, getFileIdFromUrl} from "./mapping/utils-mapping.js";

/**
 * Initialise les boutons de la liste de fichiers (visualiser et supprimer).
 * À appeler après injection du HTML contenant #file-one-list.
 * 
 */

const FILE_CONTAINER_BTNS_LIST_FILES_ID = 'file-one-list';
const URL_FILE_PREVIEW = '/file/preview/';

function getContainerBtnList(){
    return document.getElementById(FILE_CONTAINER_BTNS_LIST_FILES_ID);
}

export function initBtnListFile(urlDemandee=null) {
    const fileListContainer = getContainerBtnList();
    if (!fileListContainer) return;
    activeBtnVisualize(urlDemandee);

    // Évite de ré-attacher plusieurs fois les événements
    if (fileListContainer.dataset.listenersAttached === 'true') return;

    fileListContainer.addEventListener('click', async function (event) {
        const visualizeBtn = event.target.closest('.btn-visualize');
        const deleteBtn = event.target.closest('.btn-delete');

        // Visualiser un fichier
        if (visualizeBtn && fileListContainer.contains(visualizeBtn)) {
            event.preventDefault();
            const fileId = getIdFromBtnVisualize(visualizeBtn);
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
            const fileId = getIdFromBtnVisualize(deleteBtn);
            let nextId = fileId;
            if (isIdInUrl(fileId)) nextId = getFirstDifferentFileIdBtnVisualize(fileId);
            const result = await queryDeleteFile({file_id:fileId, filename:null});
            if (nextId != fileId){
                const newUrl = URL_FILE_PREVIEW + nextId;
                window.location.pathname = newUrl;
            }else{
                initBtnListFile();
            }
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
        const fileId = getIdFromBtnVisualize(visualizeBtn);

        fileFrontNameInput.value = text;
        fileFrontNameInput.dataset.originalValue = text;
        fileFrontNameInput.dataset.fileId = fileId;
    }

    // Initialisation de la pagination dynamique du tableau
    initChunkedTablePagination();
    // Initialisation du scroll horizontal
    initHorizontalScroll();
    // Mapping Preview
    InitMappingPreview();
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

function getIdFromBtnVisualize(btn){
    if (!btn) return null;
    return btn.dataset.fileId;
}

function getFirstDifferentFileIdBtnVisualize(currentFileId) {
    const btnsContainer = getContainerBtnList();
    if (!btnsContainer) return null;
    const btns = btnsContainer.querySelectorAll('.btn-visualize.btn-list-file');
    for (const btn of btns) {
        const fileId = getIdFromBtnVisualize(btn);
        if (fileId && fileId !== currentFileId) {
            return fileId;
        }
    }
    return null; // Aucun trouvé
}

export function activeBtnVisualize(urlDemandee=null){
    const btnsContainer = getContainerBtnList();
    if (!btnsContainer) return;
    const btns = btnsContainer.querySelectorAll('.btn-visualize.btn-list-file');
    if (!btns) return;
    const idUrl = getFileIdFromUrl(urlDemandee);
    if (!idUrl) return;

    for (const btn of btns) {
        btn.classList.remove('.active');
        if (getIdFromBtnVisualize(btn) == idUrl){
            btn.classList.add('active');
        }
    }
}