import { getEncodedFilepathMappingDatas } from "./getters-mapping.js";
import { queryRemplacementFile } from "../../loader/generate_remplacement.js";

const PHONEX_MAPPING_FIELDS_TYPES = ["soundex", "metaphone", "metaphone3"];

/**
 * Génère un fichier de remplacement à partir des informations du champ caché.
 */
export async function generateRemplacementFile(hf, filename) {
    if (!hf) return null;

    const divs = getDivsHiddenFieldDetail(hf);
    if (!divs.length) return null;

    const originalField = getOriginalFieldHiddenFieldDetail(divs);
    if (!originalField) return null;

    const encodedFilepath = getEncodedFilepathMappingDatas();
    if (!encodedFilepath) return null;

    const fileInfos = {
        encoded_filepath: encodedFilepath,
        original_field: originalField,
        filename: filename
    };

    try {
        return await queryRemplacementFile(fileInfos, "remplacement");
    } catch (e) {
        console.error("Erreur lors de la génération du fichier de remplacement :", e);
        return null;
    }
}

/**
 * Prépare les infos pour la génération d’un fichier phonétique.
 */
export async function generatePhoneticFile(hf, filename) {
    if (!hf) return null;

    const divs = getDivsHiddenFieldDetail(hf);
    if (!divs.length) return null;

    const originalField = getOriginalFieldHiddenFieldDetail(divs);
    if (!originalField) return null;

    const encodedFilepath = getEncodedFilepathMappingDatas();
    if (!encodedFilepath) return null;

    const phonetic = getPhoneticsFieldHiddenFieldDetail(divs);

    const fileInfos = {
        encoded_filepath: encodedFilepath,
        original_field: originalField,
        filename: filename,
        phonetic: phonetic
    };
    try {
        return await queryRemplacementFile(fileInfos, "phonetic");
    } catch (e) {
        console.error("Erreur lors de la génération du fichier de phonetic :", e);
        return null;
    }
}

// Helpers

function getDivsHiddenFieldDetail(hf) {
    if (!hf) return [];
    // NodeList → Array pour plus de flexibilité
    return Array.from(hf.querySelectorAll("div"));
}

function getOriginalFieldHiddenFieldDetail(divs) {
    if (!divs) return null;
    for (const div of divs) {
        if (div.getAttribute("data-field") === "original_field") {
            return div.getAttribute("data-original-value") || null;
        }
    }
    return null;
}

function getPhoneticsFieldHiddenFieldDetail(divs) {
    if (!divs) return {};
    const phonetics = {};
    for (const div of divs) {
        const dataField = div.getAttribute("data-field");
        if (PHONEX_MAPPING_FIELDS_TYPES.includes(dataField)) {
            phonetics[dataField] = getPhonexSwitchValue(div);
        }
    }
    return phonetics;
}

function getPhonexSwitchValue(div) {
    if (!div) return false;
    // Sélecteur robuste : input[type=checkbox] dans un label descendant de ce div
    const switchElement = div.querySelector("label input[type='checkbox']");
    return !!(switchElement && switchElement.checked);
}
