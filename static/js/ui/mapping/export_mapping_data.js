import { getHiddenFields,
    getMappingFileFrontNameFromFrontEnd,
    getMappingFileIdFromFrontEnd,
    getEncodedFilepathMappingDatas
} from "./getters-mapping.js";

import {
    getHiddenMappingFieldsRemplacementAllValues,
    getHiddenMappingFieldsPhoneticAllValues,
    getHiddenMappingFieldsSourceAllValues,
    getHiddenMappingFieldsFixedValueAllValues
} from "./getters-hidden-mapping-fields.js";

import {querySaveMappingFile} from "../../loader/save_mapping.js";

// Fonction principale d’export
export function exportAllMappingFieldData() {
    const hiddenFields = getHiddenFields();
    if (!hiddenFields) return {};
    let mappingFileInfos = {};

    hiddenFields.forEach(hf => {
        const category = hf.getAttribute("data-category");
        const fieldName = hf.getAttribute("data-source");
        if (!category || !fieldName) return;

        switch (category) {
            case "remplacement":
                mappingFileInfos[fieldName] = getHiddenMappingFieldsRemplacementAllValues(hf);
                break;
            case "phonetic":
                mappingFileInfos[fieldName] = getHiddenMappingFieldsPhoneticAllValues(hf);
                break;
            case "source":
                mappingFileInfos[fieldName] = getHiddenMappingFieldsSourceAllValues(hf);
                break;
            case "fixed_value":
                mappingFileInfos[fieldName] = getHiddenMappingFieldsFixedValueAllValues(hf);
                break;
            default:
                // Cas non géré, on ignore
                break;
        }
    });

    return mappingFileInfos;
}

function buildFullFileInfos(){

    return {
        "mapping_name": getMappingFileFrontNameFromFrontEnd(),
        "file_id": getMappingFileIdFromFrontEnd(),
        "encoded_data_filepath": getEncodedFilepathMappingDatas(),
        "mapping": exportAllMappingFieldData()
    }
}

// Sauvegarde (console.log ici)
export async function saveMappingFieldData(newFile=false) {
    const fileInfos = buildFullFileInfos();
    if (newFile){
        fileInfos.file_id = null;
    }
    const result = await querySaveMappingFile(fileInfos);
    if (result.success){
        console.log(result);
        if (result.new_file){
            console.log(result.new_file);
        }
    }
    if (!result.success){
        console.log(result.error);
    }
}
