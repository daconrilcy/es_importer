export function divMappingPreviewIsPresent() {
    return document.querySelectorAll('div.mapping-preview-container').length > 0;
}


export function centerElementOnAnother(elementToCenter, targetElement) {
    // Récupère les coordonnées et dimensions des deux éléments
    const targetRect = targetElement.getBoundingClientRect();
    const centerRect = elementToCenter.getBoundingClientRect();

    // Calcul du centre du target
    const targetCenterX = targetRect.left + targetRect.width / 2;
    const targetCenterY = targetRect.top + targetRect.height / 2;

    // Calcul des positions à appliquer pour centrer
    const left = targetCenterX - centerRect.width / 2 + window.scrollX;
    const top  = targetCenterY - centerRect.height / 2 + window.scrollY;

    // Applique le style
    elementToCenter.style.left = left + "px";
    elementToCenter.style.top = top + "px";
}


export function isMouseOverElement(element, mouseX, mouseY) {
    const elemUnderMouse = document.elementFromPoint(mouseX, mouseY);
    return element === elemUnderMouse || element.contains(elemUnderMouse);
}

export function cloneElement(element){
    const clone = element.cloneNode(true); // true = copie profonde
    element.parentNode.insertBefore(clone, element.nextSibling);
    return clone;
}

export function selectOrCreateOption(selectElement, value) {
    const exists = Array.from(selectElement.options).some(option => option.value === value);
    if (!exists) {
        // On crée et ajoute l’option manquante
        const newOption = document.createElement("option");
        newOption.value = value;
        newOption.text = value; // Ou ce que tu veux afficher
        selectElement.appendChild(newOption);
    }
    selectElement.value = value;
}

export function getSwitchValue(div) {
    if (!div) return false;
    // Sélecteur robuste : input[type=checkbox] dans un label descendant de ce div
    const switchElement = div.querySelector("label input[type='checkbox']");
    return !!(switchElement && switchElement.checked);
}

export function isIdInUrl(fileId){
    return window.location.href.includes(fileId);
}

export function getFileIdFromUrl(url=null) {
    if (!url){
        url = window.location.pathname;
    }
    const match = url.match(/^\/file\/preview\/([^\/]+)/);
    return match ? match[1] : null;
}