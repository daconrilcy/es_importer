import { showLoadingSpinner, hideLoadingSpinner } from "../ui/chunk_loading_spinner.js";
import { fetchTableDatasByFilePath } from "../loader/load_full_table.js";
import { tranformHtmlToData } from "../ui/inject_html_to_table.js";
import { attachTableEvents } from "../attach-table-events.js";

export async function process_table(encodedFilepath, chunkIndex, full_load = true) {
    const table = document.getElementById('csv-table');
    if (!table) return;

    showLoadingSpinner(table);

    let resultHtml = false;

    // 1. Récupération des datas du chunk 
    if (full_load) {
        resultHtml = await fetchTableDatasByFilePath(encodedFilepath, chunkIndex);
    }

    if (!resultHtml) {
        hideLoadingSpinner(table);
        return;
    }

    // 2. Injection des données dans la table
    tranformHtmlToData(resultHtml, table, full_load);

    // 3. PAS de mise à jour de la pagination

    // 4. Réinjection des js attachés à la table
    attachTableEvents();

    hideLoadingSpinner(table);
}
