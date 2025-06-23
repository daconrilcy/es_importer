/**
 * Génère un identifiant unique pour la duplication, évite les collisions (_copy, _copy2, ...).
 * @param {string} baseName - Le nom de base.
 * @returns {string} Un nom unique.
 */
function generateUniqueName(baseName) {
    let suffix = "_copy";
    let i = 1;
    let newName = baseName + suffix;
    while (
        getHiddenFieldBySourceName(newName) ||
        getMappingRowBySourceName(newName)
    ) {
        i += 1;
        newName = `${baseName}${suffix}${i}`;
    }
    return newName;
}

/**
 * Duplique un champ de mapping, crée un nouvel identifiant et rafraîchit la preview et les events.
 * @param {string} elementSourceName - Nom du champ à dupliquer.
 */
import { getHiddenFieldBySourceName, getMappingRowBySourceName } from "./getters-mapping.js";
import { cloneElement } from "./utils-mapping.js";
import { addEventButtonHiddenField, addPreviewToMappingFields, addEventButtonMappingRows } from "./events-mapping.js";

export function duplicateField(elementSourceName) {
    if (typeof elementSourceName !== "string" || !elementSourceName) return;

    const selectedHidden = getHiddenFieldBySourceName(elementSourceName);
    const selectedRow = getMappingRowBySourceName(elementSourceName);
    const newName = generateUniqueName(elementSourceName);

    // Duplique le champ caché (preview détaillée)
    if (selectedHidden && selectedHidden.parentNode) {
        const hiddenCloned = cloneElement(selectedHidden);
        hiddenCloned.setAttribute("data-source", newName);
        hiddenCloned.querySelectorAll("div").forEach(cc => {
            if (cc.getAttribute("data-field") === "name") {
                const inputName = cc.querySelector("input");
                if (inputName) {
                    inputName.setAttribute("data-original-value", newName);
                    inputName.value = newName;
                }
            }
        });
    }

    // Duplique la ligne visible (row)
    if (selectedRow && selectedRow.parentNode) {
        const clonedRow = cloneElement(selectedRow);
        clonedRow.setAttribute("data-source", newName);
        clonedRow.querySelectorAll("div").forEach(f => {
            if (f.getAttribute("data-field") === "name") {
                f.innerHTML = newName;
            }
        });
    }

    // Rafraîchit les listeners/events
    addPreviewToMappingFields();
    addEventButtonHiddenField();
    addEventButtonMappingRows();
}
