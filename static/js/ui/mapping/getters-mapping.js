const MAPPING_DROPDOWN_ROOT_ID = "dropdown-mapping-card-menu-root";
const MAPPING_DROPDOWN_SELECT_FIELD_ID = "dp_add_field_field_selection";
const MAPPING_DROPDOWN_INPUT_NAME_ID= "field_name_dp_add";
const MAPPING_DROPDOWN_INPUT_COMPL_TYPE_ID = "type_completion_add_field";
const MAPPING_DROPDOWN_INPUT_FIXED_VALUE_ID= "dp_add_field_fixed_value";
const MAPPING_FRONT_END_FRONT_NAME_INPUT_ID = "file_front_name";

import {QueryFileDataHeaders} from '../../loader/data_headers.js';
import {getDivMappingFieldValueFromInput} from './getters-hidden-mapping-fields.js';


export function getHiddenDetailMappingFieldsContainer(){
    return document.querySelector(".mapping-preview-hidden-container-modif");
}

export function getHiddenFields() {
    const hiddenFieldsContainer = getHiddenDetailMappingFieldsContainer();
    if (!hiddenFieldsContainer) return null;
    const hiddenFields = hiddenFieldsContainer.querySelectorAll(".field-preview");
    return hiddenFields.length ? hiddenFields : null;
}

export function getHiddenFieldDetail(fieldName) {
    if (!fieldName) return null;
    const hiddenFields = getHiddenFields();
    if (!hiddenFields) return null;

    return Array.from(hiddenFields).find(hf => hf.getAttribute("data-source") === fieldName) || null;
}

export function isVisibleFieldHovered() {
    const hiddenFields = getHiddenFields();
    if (!hiddenFields) return false;

    for (const hf of hiddenFields) {
        if (hf.classList.contains("visible") && hf.classList.contains("hovered")) {
            return true;
        }
    }
    return false;
}

export function getOriginalValueHiddenField(hf) {
    if (!hf) return null;

    const inputFields = getAllInputRowHiddenFields(hf);

    if (inputFields == null) return null;

    let data = {};

    inputFields.forEach(inputF => {
        const fieldName = getHiddenFieldInputName(inputF);
        const originalData = getHiddenFieldInputOriginalValue(inputF);

        if (fieldName && originalData) {
            data[fieldName] = originalData;
        }
    });

    return data;
}

export function getAllInputRowHiddenFields(hf){
    if (!hf) return null;

    const inputFields = hf.querySelectorAll(".row.field input, .row.field select");
    if (!inputFields.length) return null;

    return inputFields;
}

export function getHiddenFieldInputName(inputField){
    if (!inputField) return;

    return inputField.getAttribute("data-field");
}

export function getHiddenFieldInputOriginalValue(inputField){
    if (!inputField) return;

    return inputField.getAttribute("data-original-value");
}

export function getHiddenFieldSelectCompletionFilename(hf) {
    if (!hf) return null;
    const divs = hf.querySelectorAll("div");
    for (const div of divs) {
        if (div.getAttribute("data-field") === "filename") {
            return div.querySelector("select");
        }
    }
    return null;
}

export function getMappingFieldsContainer(){
    return document.querySelector(".mapping-preview-container .container.wrapper .container.wrapper-fields");
}

export function getMappingTitleContainer(){
    return document.querySelector(".mapping-preview-container .wrapper .wrapper-headers .under-title");
}

export function getMappingRowsFields(){
    const container = getMappingFieldsContainer();
    if (!container) return;
    return container.querySelectorAll(".row");
}

export function getHiddenFieldBySourceName(elementSourceName){
    const hiddenElements = getHiddenFields();
    let selectedHidden = null;
    hiddenElements.forEach(he => {
        const elementName = he.getAttribute("data-source");
        if (elementSourceName === elementName) {
            selectedHidden = he;
        }
    });

    return selectedHidden;

}

export function getMappingRowBySourceName(elementSourceName){
    const rowElements = getMappingRowsFields();
    let selectedRow = null;
    rowElements.forEach(re => {
        const rowSourceName = re.getAttribute("data-source");
        if (elementSourceName === rowSourceName) {
            selectedRow = re;
        }
    });

    return selectedRow;
}

export function getMappingRowDescriptionBySourceName(elementSourceName){
    const row = getMappingRowBySourceName(elementSourceName);
    if (!row) return "";
    const rowDivs = row.querySelectorAll("div");
    return getDivMappingFieldValueFromInput(rowDivs, "description");
}

export function getSourceNameFromElement(element){
    if (!element) return;
    return element.getAttribute("data-source");
}

export function getEncodedFilepathMappingDatas(){
    const container = getMappingTitleContainer();
    if (!container) return null;
    const filenameSelect = document.querySelector(".related-to select");
    if (!filenameSelect) return;
    return filenameSelect.value;
}

export function getMappingTitleDropDownMenuContainer(){
    return document.getElementById(MAPPING_DROPDOWN_ROOT_ID);
}

export function getMappingTitleDropDownMenuCategory(){
    const container = getMappingTitleDropDownMenuContainer();
    if (!container) return null;
    return container.getAttribute("data-category");
}

export function getMappingAddOptionCardContentContainer(){
    const cardContainer = getMappingTitleDropDownMenuContainer();
    if (!cardContainer) return;
    return cardContainer.querySelector(".dropdown-content");
}

export function getDataFileHeadersList(){
    const encodedFilepath = getEncodedFilepathMappingDatas();
    return QueryFileDataHeaders(encodedFilepath);
}

export function getSourceFieldSelectAdd(){
    const selectFieldToAdd = document.getElementById(MAPPING_DROPDOWN_SELECT_FIELD_ID);
    if (!selectFieldToAdd) return null;
    return selectFieldToAdd.value;
    
}

export function getFieldNameAddField(){
    const inputFieldName = document.getElementById(MAPPING_DROPDOWN_INPUT_NAME_ID);
    if (!inputFieldName) return null;
    return inputFieldName.value;
}

export function getTypeCompletionAddField(){
    const inputTypeCompletion = document.getElementById(MAPPING_DROPDOWN_INPUT_COMPL_TYPE_ID);
    if (!inputTypeCompletion) return null;
    return inputTypeCompletion.value;
}

export function getMappingDropDownFixedValue(){
    const fixedValueInput = document.getElementById(MAPPING_DROPDOWN_INPUT_FIXED_VALUE_ID);
    if (!fixedValueInput) return null;
    return fixedValueInput.value;

}

function getFrontEndFrontNameInputElement(){
    return document.getElementById(MAPPING_FRONT_END_FRONT_NAME_INPUT_ID);
}

export function getMappingFileFrontNameFromFrontEnd(){
    const frontNameElement = getFrontEndFrontNameInputElement();
    if (!frontNameElement) return null;
    return frontNameElement.value;
}

export function getMappingFileIdFromFrontEnd(){
    const frontNameElement = getFrontEndFrontNameInputElement();
    if (!frontNameElement) return null;
    return frontNameElement.getAttribute("data-file-id");
}

