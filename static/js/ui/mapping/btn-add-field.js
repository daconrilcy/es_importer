import {
    getSourceFieldSelectAdd,
    getEncodedFilepathMappingDatas,
    getTypeCompletionAddField,
    getFieldNameAddField,
    getMappingDropDownFixedValue,
    getMappingTitleDropDownMenuCategory
} from "./getters-mapping.js";
import { queryNewMappingField } from "../../loader/get_mapping_fields.js";
import { QueryFileDataHeaders } from "../../loader/data_headers.js";
import { addRowHtmlNewField, addHiddenMappingDetailHtml } from "./setters-mapping.js";
import {InitMappingPreview} from "./mapping.js";

let currentMenu = null;

export function closeMappingDropdownMenu() {
    if (currentMenu) {
        document.body.removeChild(currentMenu);
        currentMenu = null;
    }
}

export async function openMappingDropdownMenu(btn, catField) {
    closeMappingDropdownMenu();

    const encodedFilepath = getEncodedFilepathMappingDatas();
    const html = await QueryFileDataHeaders(encodedFilepath, catField);

    if (!html) {
        alert("Impossible de récupérer le menu");
        return;
    }

    // Crée le menu à partir du HTML renvoyé
    const tempDiv = document.createElement('div');
    tempDiv.innerHTML = html;
    const menu = tempDiv.firstElementChild;

    if (!menu) {
        alert("Menu vide ou non valide");
        return;
    }

    // Positionne le menu sous le bouton
    const btnRect = btn.getBoundingClientRect();
    const scrollY = window.scrollY || window.pageYOffset;
    const scrollX = window.scrollX || window.pageXOffset;

    menu.style.position = "absolute";
    menu.style.top = (btnRect.bottom + scrollY + 4) + "px";
    menu.style.left = (btnRect.left + scrollX) + "px";
    menu.style.zIndex = 10000;

    // Ajoute fermeture sur clic extérieur
    setTimeout(() => {
        document.addEventListener("mousedown", mappingOutsideClickHandler, { once: true });
    }, 0);

    // Action valider
    const validateBtn = menu.querySelector(".btn-validate");
    if (validateBtn) {
        validateBtn.onclick = async (e) => {
            e.stopPropagation();
            await AddMappingField();
            closeMappingDropdownMenu();
        };
    }

    document.body.appendChild(menu);
    currentMenu = menu;
}

function mappingOutsideClickHandler(e) {
    if (currentMenu && !currentMenu.contains(e.target)) {
        closeMappingDropdownMenu();
    }
}

async function AddMappingField() {
    const sourceField = getSourceFieldSelectAdd();
    const categoryField = getMappingTitleDropDownMenuCategory();

    let fieldName = getFieldNameAddField();
    if (!fieldName) fieldName = `${sourceField}_${categoryField}`;

    let fieldInfos = {};

    switch (categoryField) {
        case "source":
            fieldInfos = defineMappingSourceFieldInfos(fieldName, sourceField);
            break;
        case "remplacement": {
            let typeCompletion = getTypeCompletionAddField();
            if (!typeCompletion) typeCompletion = "remplacement";
            fieldInfos = defineMappingRemplacementFieldInfos(fieldName, sourceField, typeCompletion);
            break;
        }
        case "phonetic":
            fieldInfos = defineMappingPhonexFieldInfos(fieldName, sourceField);
            break;
        case "fixed_value": {
            let fixedValue = getMappingDropDownFixedValue();
            if (!fixedValue) fixedValue = "";
            fieldInfos = defineMappingFixedFieldFieldInfos(fieldName, fixedValue);
            break;
        }
        default:
            // Cas non prévu, on ne fait rien
            return;
    }
    const twoHtmlField = await queryNewMappingField(fieldInfos);
    if (twoHtmlField){
        let rowHtml = twoHtmlField.row_html;
        let hiddenDetailHtml = twoHtmlField.details_html;
        addRowHtmlNewField(rowHtml);
        addHiddenMappingDetailHtml(hiddenDetailHtml);
        InitMappingPreview();
    } 
}

function defineMappingSourceFieldInfos(fieldName, sourceField) {
    return {
        name: fieldName,
        category: "source",
        source_field: sourceField,
        mapped: true,
        type: "text",
        analyzer: "standard"
    };
}

function defineMappingRemplacementFieldInfos(fieldName, sourceField, typeCompletion) {
    return {
        name: fieldName,
        category: "remplacement",
        type_completion: typeCompletion,
        original_field: sourceField,
        column_names: [sourceField, `${sourceField}_new`],
        keep_original: true,
        use_first_column: false
    };
}

function defineMappingPhonexFieldInfos(fieldName, sourceField) {
    return {
        name: fieldName,
        category: "phonetic",
        type_completion: "phonetic",
        original_field: sourceField,
        column_names: [sourceField],
        phonetic: { soundex: false, metaphone: false, metaphone3: false }
    };
}

function defineMappingFixedFieldFieldInfos(fieldName, value) {
    return {
        name: fieldName,
        category: "fixed_value",
        value: value
    };
}
