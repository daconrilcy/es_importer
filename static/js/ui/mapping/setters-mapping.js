import {
    getAllInputRowHiddenFields,
    getHiddenFieldInputName,
    getHiddenFieldInputOriginalValue,
    getMappingFieldsContainer,
    getHiddenDetailMappingFieldsContainer,
    getHiddenFieldSelectCompletionFilename
} from "./getters-mapping.js";

import {selectOrCreateOption} from "./utils-mapping.js";

export function refillOriginalData(hf, originalData) {
    if (!hf || !originalData) return;

    const inputFields = getAllInputRowHiddenFields(hf);

    inputFields.forEach(inputF => {
        const name = getHiddenFieldInputName(inputF);
        const originalValue = getHiddenFieldInputOriginalValue(inputF);
        if (name && originalValue !== undefined) {
            setValueToInput(originalValue, inputF);
        }
    });
}

function setValueToInput(value, inputF) {
    if (!inputF) return;

    const tag = inputF.tagName.toLowerCase();
    if (!(tag === 'input' || tag === 'select')) return;

    if (tag === 'input') {
        setValueToInputText(value, inputF);
    } else if (tag === 'select') {
        setValueToSelect(value, inputF);
    }
}

function setValueToInputText(value, inputF) {
    inputF.value = value;
}

function setValueToSelect(valueToPut, inputF) {
    if ([...inputF.options].some(opt => opt.value === valueToPut)) {
        inputF.value = valueToPut;
    }
}

export function addRowHtmlNewField(HtmlRowNewField) {
    if (!HtmlRowNewField) return;
    const fieldContainer = getMappingFieldsContainer();
    if (!fieldContainer) return;

    // Ajoute le HTML à la fin du container, sans toucher aux balises existantes
    fieldContainer.insertAdjacentHTML('beforeend', HtmlRowNewField);
}

export function addHiddenMappingDetailHtml(hiddenDetailHtml){
    if (!hiddenDetailHtml) return;
    const hiddenMappingDetailContainer = getHiddenDetailMappingFieldsContainer();
    if (!hiddenMappingDetailContainer) return;
    hiddenMappingDetailContainer.insertAdjacentHTML('beforeend', hiddenDetailHtml);
}

export function hfMappingFieldNewFilenameSetSelected(hf, newFileName){
    if (!newFileName || !hf) return;

    let selectFilename = getHiddenFieldSelectCompletionFilename(hf);
    if (!selectFilename) return;
    selectOrCreateOption(selectFilename, newFileName);

    selectFilename.classList.add('select-flash');
}