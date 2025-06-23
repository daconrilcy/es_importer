import { getHiddenFieldDetail, getHiddenFields,getMappingRowsFields } from "./getters-mapping.js";
import { showHiddenField, hideAllHiddenFields } from "./showhide-mapping.js";
import { hfBtnModify, hfBtnAccept, hfBtnRevert, hfBtnDuplicate, hfBtnDelete,hfBtnDownload,hfBtnGenerate } from "./hf-btn-function.js";
import {mappingRowModify, duplicateMappingField, deleteMappingField} from "./mrows-btn.js";
import {openMappingDropdownMenu} from "./btn-add-field.js";
import {saveMappingFieldData} from "./export_mapping_data.js";

// 🧠 Stockage des listeners pour chaque élément
const attachedListeners = new WeakMap();

function safeAddEventListener(el, type, handler) {
    const current = attachedListeners.get(el) || [];

    // Supprime les handlers déjà ajoutés pour ce type
    current
        .filter(l => l.type === type)
        .forEach(l => el.removeEventListener(l.type, l.handler));

    el.addEventListener(type, handler);
    attachedListeners.set(el, [...current.filter(l => l.type !== type), { type, handler }]);
}

// 📍 Suivi position souris pour `elementFromPoint`
let mouseX = 0, mouseY = 0;
document.addEventListener("mousemove", e => {
    mouseX = e.clientX;
    mouseY = e.clientY;
});

export function getLastMousePosition() {
    return { clientX: mouseX, clientY: mouseY };
}

// 🧩 Variables globales pour affichage caché
let currentVisible = null;
let hideTimeout = null;

// 🔍 Logique d'affichage au survol
export function addPreviewToMappingFields() {
    const mainContainer = document.querySelector(".preview-json");
    if (!mainContainer) return;

    const fieldContainer = document.querySelector(".wrapper-fields");
    if (!fieldContainer) return;

    const fieldsRows = fieldContainer.querySelectorAll(".row .fieldhover");
    if (!fieldsRows.length) return;

    fieldsRows.forEach(row => {
        const fieldName = row.getAttribute("data-source");
        const hiddenFieldDetail = getHiddenFieldDetail(fieldName);
        if (!hiddenFieldDetail) return;

        // Ajout des listeners en toute sécurité
        safeAddEventListener(row, "mouseenter", () => {
            clearTimeout(hideTimeout);
            currentVisible = hiddenFieldDetail;
            showHiddenField(row, hiddenFieldDetail);
        });

        safeAddEventListener(row, "mouseleave", () => {
            hideWithDelay();
        });

        safeAddEventListener(hiddenFieldDetail, "mouseenter", () => {
            clearTimeout(hideTimeout);
        });

        safeAddEventListener(hiddenFieldDetail, "mouseleave", () => {
            hideWithDelay();
        });
    });
}

// ⏳ Masquage différé
function hideWithDelay() {
    hideTimeout = setTimeout(() => {
        if (!currentVisible) return;

        const { clientX, clientY } = getLastMousePosition();
        const hoveredEl = document.elementFromPoint(clientX, clientY);
        const stillInside = currentVisible.contains(hoveredEl);

        if (!stillInside) {
            hideAllHiddenFields();
            currentVisible = null;
        }
    }, 100);
}

// 🔘 Gestion des boutons des hidden fields
export function addEventButtonHiddenField() {
    const hiddenFields = getHiddenFields();
    if (!hiddenFields) return;

    hiddenFields.forEach(hf => {
        const btns = hf.querySelectorAll(".glyphicon");

        btns.forEach(btn => {
            if (btn.classList.contains("glyphicon-modify")) {
                safeAddEventListener(btn, "click", () => hfBtnModify(hf));
            } else if (btn.classList.contains("glyphicon-modify-accept")) {
                safeAddEventListener(btn, "click", () => hfBtnAccept(hf));
            } else if (btn.classList.contains("glyphicon-modify-revert")) {
                safeAddEventListener(btn, "click", () => hfBtnRevert(hf));
            } else if (btn.classList.contains("glyphicon-plus")) {
                safeAddEventListener(btn, "click", () => hfBtnDuplicate(hf));
            } else if (btn.classList.contains("glyphicon-remove")) {
                safeAddEventListener(btn, "click", () => hfBtnDelete(hf));
            } else if (btn.classList.contains("glyphicon-download")) {
                safeAddEventListener(btn, "click", () => hfBtnDownload(btn));
            } else if (btn.classList.contains("glyphicon-drop")){
                safeAddEventListener(btn, "click", () => hfBtnGenerate(hf));
            }

        });
    });
}

// 🔘 Gestion des boutons des rows
export function addEventButtonMappingRows() {
    const mappingRows = getMappingRowsFields();
    if (!mappingRows) return;

    mappingRows.forEach(mr => {
        const btns = mr.querySelectorAll(".glyphicon");

        btns.forEach(btn => {
            if (btn.classList.contains("glyphicon-modify")) {
                safeAddEventListener(btn, "click", () => mappingRowModify(mr));
            } else if (btn.classList.contains("glyphicon-plus")) {
                safeAddEventListener(btn, "click", () => duplicateMappingField(mr));
            } else if (btn.classList.contains("glyphicon-remove")) {
                safeAddEventListener(btn, "click", () => deleteMappingField(mr));
            }
        });
    });
}


// Gestion des boutons Add Fields
export async function initMappingDropdownMenus() {
    document.querySelectorAll('.col-btn button[data-action]').forEach(btn => {
        safeAddEventListener(btn, "click", (e) => {
            e.stopPropagation();
            const action = btn.getAttribute("data-action");
            if (action == "save-mapping-file"){
                saveMappingFieldData(false);
            }else if(action == "save-mapping-new-file"){
                saveMappingFieldData(true);
            }else{
                openMappingDropdownMenu(btn, action);
            }
            
        });
    });
}