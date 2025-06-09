import { process_table } from "../processes/process_table.js";
import { injectGetPhoneticToFile } from "../loader/inject_phonetic.js";

/**
 * Initialise les options d’en-tête CSV :
 * - Attache les listeners sur les boutons d’entête CSV.
 * - Attache les listeners sur la card d’options.
 */
export function initCsvHeaderOptions() {
    addBtnHeadersListeners();
    addListenerToHeaderOptionCard();
}

/**
 * Attache un listener sur chaque bouton d’entête CSV (classe .btn-csv-options).
 * Quand on clique sur un en-tête, affiche ou masque la card d’options associée.
 */
function addBtnHeadersListeners() {
    const table = document.querySelector('table');
    if (!table) return;
    table.querySelectorAll('.btn-csv-options').forEach(btn =>
        btn.addEventListener('click', () => toggleCarHeaderOption(btn))
    );
}

/**
 * Affiche ou masque la card d’options sous le bouton ciblé.
 * Gère la position, le champ actif, et les classes CSS.
 */
function toggleCarHeaderOption(target) {
    if (!target) return;
    const card = document.getElementById('header-option-card');
    if (!card) return;

    // Calcule la position d’affichage de la card sous le bouton
    const rect = target.getBoundingClientRect();
    const header = target.getAttribute("data-field");
    const current = card.getAttribute("data-field");

    // Si déjà visible sur le même champ, on masque
    if (card.classList.contains("visible") && current === header) {
        card.classList.remove("visible");
        target.classList.remove('active');
    } else {
        // Positionne la card, l’associe au header ciblé
        Object.assign(card.style, {
            left: `${rect.left}px`,
            top: `${rect.bottom + window.scrollY + 4}px`
        });
        setCardHeaderAttributes(target, card);
        removeClassActiveHeaders();
        card.classList.add("visible");
        target.classList.add('active');
    }
}

/**
 * Supprime toutes les classes d’état sur tous les boutons d’entête (active, flash-red, flash-green).
 */
function removeClassActiveHeaders() {
    document.querySelectorAll('.btn-csv-options').forEach(btn =>
        btn.classList.remove('active', 'flash-red', 'flash-green')
    );
}

/**
 * Copie les attributs data-* du header ciblé vers la card d’option (data-field, data-filepath, data-sep).
 */
function setCardHeaderAttributes(header, card) {
    ["data-field", "data-filepath", "data-sep"].forEach(attr =>
        card.setAttribute(attr, header.getAttribute(attr))
    );
}

/**
 * Attache les listeners sur les boutons de la card d’option :
 * - .close masque la card.
 * - .validate lance l’injection phonétique et le refresh du tableau.
 */
function addListenerToHeaderOptionCard() {
    const card = document.getElementById('header-option-card');
    if (!card) return;
    card.querySelectorAll('.btn').forEach(btn => {
        if (btn.classList.contains('close')) {
            btn.addEventListener("click", closeHeaderOptionCard);
        }
        if (btn.classList.contains('validate')) {
            btn.addEventListener("click", addPhoneticColumnToFile);
        }
    });
}


function closeHeaderOptionCard(){
    const card = document.getElementById('header-option-card');
    if (!card) return;
    card.classList.remove('visible');
    removeClassActiveHeaders();
}


/**
 * Ajoute une colonne phonétique via l’API, refresh le tableau, et gère les feedbacks visuels.
 */
async function addPhoneticColumnToFile() {
    const card = document.getElementById('header-option-card');
    if (!card) return;
    // Récupère les infos du champ à modifier
    const [filepath, field, sep] = ["data-filepath", "data-field", "data-sep"].map(attr => card.getAttribute(attr));
    const phonetic = getAllPhoneticValues();
    const previousFields = getFieldsMap();

    // Envoie la demande d’injection phonétique
    let result = await injectGetPhoneticToFile(phonetic, filepath, field, sep);
    const btnToFlash = getBtnHeaderByFieldName(field);

    // Si KO => flash rouge sur le bouton concerné
    if (!result) {
        removeClassActiveHeaders();
        if (btnToFlash) btnToFlash.classList.add('flash-red');
        return;
    }

    // Si OK => refresh table, ferme la card, flash vert sur nouveaux champs
    await process_table(filepath, 0, true);
    card.classList.remove('visible');
    removeClassActiveHeaders();
    if (btnToFlash) addGreenFlashClean(field, previousFields);
}

/**
 * Récupère les valeurs des switches (Soundex, Metaphone, Double Metaphone) dans la card.
 */
function getAllPhoneticValues() {
    return {
        "soundex": isChecked("switch-soundex"),
        "metaphone": isChecked("switch-metaphone"),
        "metaphone3": isChecked("switch-dblmetaphone")
    };
}

/**
 * Renvoie true/false selon l’état du switch avec l’ID donné.
 */
const isChecked = id => (document.getElementById(id)?.checked) ?? false;

/**
 * Retourne le bouton d’entête pour un field donné (sinon null).
 */
function getBtnHeaderByFieldName(field) {
    return getFieldsMap()[field] || null;
}

/**
 * Crée une map {field: btn} pour tous les boutons d’entête du tableau courant.
 */
function getFieldsMap() {
    const fieldsMap = {};
    document.querySelectorAll('.btn-csv-options').forEach(btn => {
        const field = btn.getAttribute("data-field");
        if (field) fieldsMap[field] = btn;
    });
    return fieldsMap;
}

/**
 * Compare deux maps d’entête et retourne les nouveaux boutons ajoutés.
 */
function getNewFields(oldMap) {
    const currentMap = getFieldsMap();
    return Object.keys(currentMap)
        .filter(field => !(field in oldMap))
        .map(field => currentMap[field]);
}

/**
 * Ajoute l’effet flash vert sur le bouton principal et tous les nouveaux champs ajoutés.
 */
function addGreenFlashClean(initialField, oldFieldsMap) {
    let addedFields = getNewFields(oldFieldsMap);
    const btn = getBtnHeaderByFieldName(initialField);
    if (!btn) return;
    btn.classList.add('flash-green');
    addedFields.forEach(newField => newField.classList.add('flash-green'));
}
