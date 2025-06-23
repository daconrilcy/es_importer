import { addPreviewToMappingFields,addEventButtonHiddenField,addEventButtonMappingRows, initMappingDropdownMenus } from "./events-mapping.js";
import { divMappingPreviewIsPresent } from "./utils-mapping.js";

export function InitMappingPreview() {
    if (!divMappingPreviewIsPresent()) return;
    addPreviewToMappingFields();
    addEventButtonHiddenField();
    addEventButtonMappingRows();
    initMappingDropdownMenus();
}