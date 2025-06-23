import { getSwitchValue } from "./utils-mapping.js";
import { getMappingRowDescriptionBySourceName } from "./getters-mapping.js";

const PHONEX_MAPPING_FIELDS_TYPES = ["soundex", "metaphone", "metaphone3"];

// ----------- Helpers génériques -----------
function getDivMappingFieldByAttributeName(divs, attrName, valueSearch) {
    if (!divs || !attrName || !valueSearch) return null;
    for (const div of divs) {
        if (div.getAttribute(attrName) === valueSearch) return div;
    }
    return null;
}

function getDivMappingHiddenRowCategory(hf){
    if (!hf) return "";
    return hf.getAttribute("data-category");
}

function getDivMappingFieldByType(divs, typeValue) {
    return getDivMappingFieldByAttributeName(divs, "data-field", typeValue);
}

function getDivMappingFieldValueByInputType(divs, typeValue, inputType) {
    if (!divs || !typeValue || !inputType) return null;
    const div = getDivMappingFieldByType(divs, typeValue);
    if (!div) return null;
    const inputElement = div.querySelector(inputType);
    return inputElement ? inputElement.value : null;
}

export function getDivMappingFieldValueFromInput(divs, typeValue) {
    return getDivMappingFieldValueByInputType(divs, typeValue, "input");
}

function getDivMappingFieldValueFromSelect(divs, typeValue) {
    return getDivMappingFieldValueByInputType(divs, typeValue, "select");
}

// ----------- Champs communs -----------
function getHiddenMappingFieldsOriginalFieldValue(divs) {
    const div = getDivMappingFieldByType(divs, "original_field");
    return div ? div.innerHTML.trim() : null;
}

function getHiddenMappingFieldsNameValue(divs) {
    return getDivMappingFieldValueFromInput(divs, "name");
}

function getHiddenMappingFieldsFilenameValue(divs) {
    return getDivMappingFieldValueFromSelect(divs, "filename");
}

// ----------- Remplacement -----------
function getMappingHiddenFieldTypeValue(divs) {
    return getDivMappingFieldValueFromInput(divs, "type");
}

function getHiddenMappingFieldsKeepOriginalValue(divs) {
    return getDivMappingFieldValueFromSelect(divs, "keep_original");
}

function getHiddenMappingFieldsUseFirstColumnValue(divs) {
    return getDivMappingFieldValueFromSelect(divs, "use_first_column");
}

export function getHiddenMappingFieldsRemplacementAllValues(hf) {
    if (!hf) return {};
    const divs = hf.querySelectorAll("div");
    if (!divs) return {};
    const fieldName = getHiddenMappingFieldsNameValue(divs);
    return {
        category: getDivMappingHiddenRowCategory(hf),
        type_completion: getMappingHiddenFieldTypeValue(divs),
        original_field: getHiddenMappingFieldsOriginalFieldValue(divs),
        name: fieldName,
        keep_original: getHiddenMappingFieldsKeepOriginalValue(divs),
        filename: getHiddenMappingFieldsFilenameValue(divs),
        use_first_column: getHiddenMappingFieldsUseFirstColumnValue(divs),
        description: getMappingRowDescriptionBySourceName(fieldName)
    };
}

// ----------- Phonetic -----------
function getHiddenMappingFieldsPhoneticColumnValue(divs) {
    if (!divs) return {};
    const phonetics = {};
    for (const div of divs) {
        const dataField = div.getAttribute("data-field");
        if (PHONEX_MAPPING_FIELDS_TYPES.includes(dataField)) {
            phonetics[dataField] = getSwitchValue(div);
        }
    }
    return phonetics;
}

export function getHiddenMappingFieldsPhoneticAllValues(hf) {
    if (!hf) return {};
    const divs = hf.querySelectorAll("div");
    if (!divs) return {};
    const fieldName = getHiddenMappingFieldsNameValue(divs);
    return {
        category: getDivMappingHiddenRowCategory(hf),
        original_field: getHiddenMappingFieldsOriginalFieldValue(divs),
        type_completion: "phonetic",
        name: fieldName,
        filename: getHiddenMappingFieldsFilenameValue(divs),
        phonetic: getHiddenMappingFieldsPhoneticColumnValue(divs),
        description: getMappingRowDescriptionBySourceName(fieldName)
    };
}

// ----------- Fixed value -----------
function getHiddenMappingFieldsFixedValue(divs) {
    return getDivMappingFieldValueFromInput(divs, "value");
}

export function getHiddenMappingFieldsFixedValueAllValues(hf) {
    if (!hf) return {};
    const divs = hf.querySelectorAll("div");
    if (!divs) return {};
    const fieldName = getHiddenMappingFieldsNameValue(divs);
    return {
        category: getDivMappingHiddenRowCategory(hf),
        name: fieldName,
        value: getHiddenMappingFieldsFixedValue(divs),
        description: getMappingRowDescriptionBySourceName(fieldName)
    };
}

// ----------- Source -----------
function getHiddenMappingFieldsTypeSelectValue(divs) {
    return getDivMappingFieldValueFromSelect(divs, "type");
}

function getHiddenMappingFieldsMappedSelectValue(divs) {
    return getDivMappingFieldValueFromSelect(divs, "mapped");
}

function getHiddenMappingFieldsAnalyzerSelectValue(divs) {
    return getDivMappingFieldValueFromSelect(divs, "analyzer");
}

export function getHiddenMappingFieldsSourceAllValues(hf) {
    if (!hf) return {};
    const divs = hf.querySelectorAll("div");
    if (!divs) return {};
    const fieldName = getHiddenMappingFieldsNameValue(divs);
    return {
        category: getDivMappingHiddenRowCategory(hf),
        source_field: getHiddenMappingFieldsOriginalFieldValue(divs),
        name: fieldName,
        type: getHiddenMappingFieldsTypeSelectValue(divs),
        mapped: getHiddenMappingFieldsMappedSelectValue(divs),
        analyzer: getHiddenMappingFieldsAnalyzerSelectValue(divs),
        description: getMappingRowDescriptionBySourceName(fieldName)
    };
}
