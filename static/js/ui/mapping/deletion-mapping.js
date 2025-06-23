/**
 * Supprime un champ de mapping (row + hidden field) de l’interface et nettoie les listeners associés.
 * Rafraîchit la preview et les events pour garantir la cohérence UI.
 * @param {string} fieldSourceName - Identifiant unique du champ à supprimer.
 */
import { getHiddenFieldBySourceName, getMappingRowBySourceName } from "./getters-mapping.js";
import { addEventButtonHiddenField, addPreviewToMappingFields, addEventButtonMappingRows } from "./events-mapping.js";

export function deleteMapping(fieldSourceName) {
    if (typeof fieldSourceName !== 'string' || !fieldSourceName) return;

    // Suppression du champ caché
    const selectedHidden = getHiddenFieldBySourceName(fieldSourceName);
    if (selectedHidden && selectedHidden.parentNode) {
        selectedHidden.parentNode.removeChild(selectedHidden);
    }

    // Suppression de la ligne visible
    const selectedMappingRow = getMappingRowBySourceName(fieldSourceName);
    if (selectedMappingRow && selectedMappingRow.parentNode) {
        selectedMappingRow.parentNode.removeChild(selectedMappingRow);
    }

    // Rafraîchit la preview et les événements pour assurer la réactivité
    addPreviewToMappingFields();
    addEventButtonHiddenField();
    addEventButtonMappingRows();
}
