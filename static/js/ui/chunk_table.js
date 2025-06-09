import { showLoadingSpinner, hideLoadingSpinner } from "./chunk_loading_spinner.js";
import {attachTableEvents} from "./../attach-table-events.js";

let currentEncodedFilePath = null;

/**
 * Initialise la pagination si la table existe.
 * À appeler après chaque injection de #csv-table.
 */
export function initChunkedTablePagination() {
    const table = document.getElementById('csv-table');
    if (!table) return;

    currentEncodedFilePath = table.dataset.filepath;
    if (!currentEncodedFilePath) return;

    attachTableEvents();
}

/**
 * Charge un nouveau chunk de lignes et met à jour la pagination.
 * @param {number} newChunkIndex - Index du chunk à charger
 * @param {string} encodedFilePath - Chemin du fichier encodé
 */
export async function loadChunk(newChunkIndex, encodedFilePath) {
    if (newChunkIndex < 0) return;

    const table = document.getElementById('csv-table');
    if (!table) return;

    showLoadingSpinner(table);

    try {
        // 1. Récupération des lignes du chunk
        const chunkUrl = `/file/chunk-rows/${encodedFilePath}/${newChunkIndex}`;
        const chunkRes = await fetch(chunkUrl);
        if (!chunkRes.ok) throw new Error('Erreur de chargement des données');

        const chunkHtml = await chunkRes.text();
        const tempTable = document.createElement('table');
        tempTable.innerHTML = chunkHtml;

        const newTbody = tempTable.querySelector('tbody');
        const tbody = table.querySelector('tbody');
        if (tbody && newTbody) {
            tbody.innerHTML = newTbody.innerHTML;
        }

        // 2. Mise à jour de la pagination
        const numChunks = parseInt(table.dataset.numChunks, 10);
        const chunkSize = parseInt(table.dataset.chunkSize, 10);
        const fileId = table.dataset.fileId;

        const paginationUrl = `/file/pagination-data/${newChunkIndex}/${numChunks}/${chunkSize}`;
        const pagRes = await fetch(paginationUrl);
        if (pagRes.ok) {
            const pagHtml = await pagRes.text();
            const chunkBar = document.getElementById('chunkBar');
            if (chunkBar) {
                chunkBar.innerHTML = pagHtml;

                // 🔁 Réattacher immédiatement les nouveaux événements
                attachTableEvents();
            }
        }

        // 3. Mise à jour de l’URL
        table.dataset.chunkIndex = newChunkIndex;
        history.pushState(null, '', `/file/preview/${fileId}/${newChunkIndex}`);

    } catch (err) {
        console.error('Erreur lors du chargement du chunk :', err);
        alert('Impossible de charger les données du fichier.');
    } finally {
        hideLoadingSpinner();
    }
}
