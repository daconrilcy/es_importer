import { attachMenuEventListeners } from "./menu.js";
import { initializeDropzone } from "./dropzone-init.js";

export async function loadPage(url, pushState = true) {
    try {
        const response = await fetch(url, { headers: { "X-Requested-With": "XMLHttpRequest" } });
        if (!response.ok) throw new Error(`Erreur HTTP : ${response.status}`);
        document.getElementById("content").innerHTML = await response.text();
        if (pushState) history.pushState({ url }, "", url);
        initializeDynamicComponents(url);
    } catch (error) {
        console.error("Erreur de chargement :", error);
    }
}

export function initializeDynamicComponents(url = "") {
    attachMenuEventListeners();
    if (url.includes("import")) initializeDropzone();
}
