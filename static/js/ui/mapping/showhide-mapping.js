import { getHiddenFields, getMappingRowBySourceName, getSourceNameFromElement } from "./getters-mapping.js";
import { centerElementOnAnother } from "./utils-mapping.js";
import { getLastMousePosition } from "./events-mapping.js";

export function hideAllHiddenFields() {
    const hiddenFields = getHiddenFields();
    if (!hiddenFields) return;
    hiddenFields.forEach(hf => hf.classList.remove("visible"));
}

export function showHiddenField(divHover, hiddenField) {
    hideAllHiddenFields();
    const sourceName = getSourceNameFromElement(divHover);
    hiddenField.classList.add("visible");
    const row = getMappingRowBySourceName(sourceName);
    centerElementOnAnother(hiddenField, row);
}

export function isMouseOverNoHoverElement(){
    const { clientX, clientY } = getLastMousePosition();
    const hoveredEl = document.elementFromPoint(clientX, clientY);
    const parentHv = hoveredEl.parentNode;
    if (hoveredEl.classList.contains("nohover") || parentHv.classList.contains("nohover")){
        return true
    }
    return false;
}
