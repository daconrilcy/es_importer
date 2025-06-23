import {getHiddenFields, getOriginalValueHiddenField, getHiddenFieldSelectCompletionFilename} from "./getters-mapping.js";
import {refillOriginalData, hfMappingFieldNewFilenameSetSelected} from "./setters-mapping.js";
import {duplicateField} from "./duplication.js";
import {deleteMapping} from "./deletion-mapping.js";
import {downloadCompletion} from "./../../loader/down_file_completion.js";
import {generateRemplacementFile, generatePhoneticFile} from "./completion_file_generation.js";
import { initMappingDropdownMenus } from "./events-mapping.js";


export function hfBtnModify(hf){
    if (!hf) return;
    if (hf.classList.contains("modify")){
        hf.classList.remove("modify");
        removeBlocked();
    }else{
        hf.classList.add("modify");
        addBlocked();
        hf.classList.remove("blocked");
    }
}

export function hfBtnAccept(hf){
     if (!hf) return;
     hf.classList.remove("modify");
     removeBlocked();
}

export function hfBtnRevert(hf){
    const originalData = getOriginalValueHiddenField(hf);
    refillOriginalData(hf, originalData);
    hf.classList.remove("modify");
    removeBlocked();
}

export function hfBtnDuplicate(hf){
    const FieldSourceName = hf.getAttribute("data-source");
    duplicateField(FieldSourceName);
}

export function hfBtnDelete(hf){
    const FieldSourceName = hf.getAttribute("data-source");
    deleteMapping(FieldSourceName);

}

export function hfBtnDownload(btn){
    const filename = btn.getAttribute("data-filename");
    if(!filename) return;
    downloadCompletion(filename);
}

export async function hfBtnGenerate(hf) {
    if (!hf) return;
    let selectFilename = getHiddenFieldSelectCompletionFilename(hf);
    if (!selectFilename) return;
    selectFilename.classList.remove('select-flash');

    const category = hf.getAttribute("data-category");
    if (!category) return;

    let filename = selectFilename.value;

    let newFileName = null;
    switch (category) {
        case "remplacement":
            {
                newFileName = await generateRemplacementFile(hf, filename);
                break;
            }
        case "phonetic":
            {
                newFileName = await generatePhoneticFile(hf, filename);
                break;
            }
        default:
            console.warn(`Catégorie non prise en charge : ${category}`);
            return;
    }

    if (newFileName){
        hfMappingFieldNewFilenameSetSelected(hf, newFileName);
        initMappingDropdownMenus();
    }
}


function addBlocked(){
    let hFs = getHiddenFields();
    hFs.forEach(hf=>{
        hf.classList.add("blocked");
    });
}

function removeBlocked(){
    let hFs = getHiddenFields();
    hFs.forEach(hf=>{
        hf.classList.remove("blocked");
    })
}

