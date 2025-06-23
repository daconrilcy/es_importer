import { initDarkMode } from "darkmode";
import { initChunkedTablePagination } from "chunk_table";
import { initRadioGroups } from "radio-group";
import { setActiveMenuItemFromPath } from "menu";
import { initSpaNavigation } from "./navigation/spa-router.js";
import { initHorizontalScroll } from "./ui/scroll-horizontal.js";
import { initModifyTitle } from "./ui/modify-title.js";
import { initBtnListFile } from "./ui/btn-list-file.js";
import { InitMappingPreview } from "./ui/mapping/mapping.js";

document.addEventListener('DOMContentLoaded', () => {
    initDarkMode();
    initChunkedTablePagination();
    initRadioGroups();
    initSpaNavigation();
    initHorizontalScroll();
    initModifyTitle();
    initBtnListFile();
    InitMappingPreview();
    
    history.replaceState(
        { html: document.getElementById('content').innerHTML, url: location.pathname },
        '',
        location.pathname
    );
    setActiveMenuItemFromPath();

    // Initialisation Dropzone si on est sur /upload
    if (window.location.pathname === '/upload') {
        import('./dropzone-init.js').then(mod => {
            mod.initializeDropzone();
        });
    }
   
});