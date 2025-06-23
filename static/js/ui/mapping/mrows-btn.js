import {getHiddenFieldBySourceName} from "./getters-mapping.js";
import { duplicateField } from "./duplication.js";
import { deleteMapping } from "./deletion-mapping.js";


function getLinkedHiddenField(row){
    const sourceName = row.getAttribute("data-source");
    return getHiddenFieldBySourceName(sourceName);
}

export function mappingRowModify(row){
    let hiddenField = getLinkedHiddenField(row)
    hiddenField.classList.add("modify");
}

export function duplicateMappingField(row){
    const sourceName = row.getAttribute("data-source");
    duplicateField(sourceName);

}

export function deleteMappingField(row){
    const sourceName = row.getAttribute("data-source");
    deleteMapping(sourceName);
}