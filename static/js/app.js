import { loadPage } from "./navigation.js";
import { initializeDynamicComponents } from "./navigation.js";
import { initFileRowEvents } from "./list_files.js";
import { initMappingPreviewEvents} from "./mapping_preview.js";

document.addEventListener("DOMContentLoaded", () => {
    initPage(); // première initialisation

    // liens internes SPA
    document.addEventListener("click", function (event) {
        const link = event.target.closest("a");
        if (link && link.getAttribute("href") && link.origin === window.location.origin) {
            console.log("SPA navigation vers :", link.getAttribute("href"));
            event.preventDefault();
            loadPage(link.getAttribute("href")).then(() => {
                initPage(); // réinitialise les events après chargement dynamique
                initPreview();
            });
        }
    });

    // navigation arrière / avant
    window.addEventListener("popstate", (event) => {
        if (event.state?.url) {
            loadPage(event.state.url, false).then(() => {
                initPage();
            });
        }
    });

    document.addEventListener("components:reinit", () => {
        initPage();
    });
    document.addEventListener("preview:reinit", () => {
        initMappingPreviewEvents();
    });

});

function initPage() {
    let itrow = initFileRowEvents();
    initializeDynamicComponents();

    // si tu as d’autres composants
}
function initPreview(){
    initMappingPreviewEvents();
}
