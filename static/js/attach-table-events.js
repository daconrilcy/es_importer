import { initCsvHeaderOptions } from './ui/csv-headers-options.js';
import {loadChunk} from './ui/chunk_table.js';

/**
 * Attache les événements liés aux tables de visualisation de CSV
 */
export function attachTableEvents() {
    paginationEvent();
    initCsvHeaderOptions();
}

function paginationEvent() {
    const tables = document.getElementsByTagName('table');
    if (!tables.length) return;

    const table = tables[0];
    const encodedFilePath = table.getAttribute("data-filepath");
    if (!encodedFilePath) return;

    const chunkBar = document.getElementById('chunkBar');
    if (!chunkBar) return;

    const paginationBtns = chunkBar.querySelectorAll('button.page-link[data-chunk]');
    paginationBtns.forEach(btn => {
        const chunkIndex = btn.getAttribute('data-chunk');
        const newBtn = btn.cloneNode(true); // évite les doublons d'événements
        btn.replaceWith(newBtn);
        newBtn.addEventListener('click', () => {
            const index = parseInt(chunkIndex, 10);
            if (!isNaN(index)) {
                loadChunk(index, encodedFilePath);
            }
        });
    });
}
