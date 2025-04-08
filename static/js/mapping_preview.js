import {FILETYPENAMES, LIST_FILE_CONTAINER_ID, PREVIEW_FIELDS_CONTAINER_ID, PREVIEW_CONTAINER_ID, FIELDS_LIST_ID,
    SELECT_DATAS_FILE_ID, SELECT_FIELD_TO_ADD_ID, 
    BTN_UPDATE_MAPPING_ID, BTN_ADD_FIELD_ID, BTN_SAVE_FILE_ID, BTN_DELETE_FILE_ID
} from './config.js';
export function initMappingPreviewEvents() {
    const listFileContainer = document.getElementById(LIST_FILE_CONTAINER_ID);
    const listFieldContainer = document.getElementById(PREVIEW_FIELDS_CONTAINER_ID);

    if (!listFieldContainer) {
        return;
    }
    const rowFields = listFieldContainer.querySelectorAll('.field-preview');
    if (!rowFields){
        return;
    }
    rowFields.forEach(row => initPreviewRowEvents(row));
    const selectFile = document.getElementById(SELECT_DATAS_FILE_ID);
    if (selectFile) {
        selectFile.addEventListener('change', (e) => {
            const selectedFile = e.target.value;
            const OriginalFile = e.target.getAttribute('data-original');
            const btnUpdate = document.getElementById(BTN_UPDATE_MAPPING_ID);
            if (btnUpdate) {
                if (selectedFile !== OriginalFile) {
                    btnUpdate.classList.remove('hidden');
                } else {
                    btnUpdate.classList.add('hidden');
                }
            }
        });
    }

    const btnDeleteFile = document.getElementById(BTN_DELETE_FILE_ID);
    if (btnDeleteFile) {
        btnDeleteFile.addEventListener('click', (e) => {
            e.preventDefault();
            const filename = btnDeleteFile.dataset.filename;
            const file_id = btnDeleteFile.dataset.id;
            const fileType = btnDeleteFile.dataset.file_type;
            deleteFile(filename, file_id, fileType, listFileContainer);
        });
    }

    const btnSaveFile = document.getElementById(BTN_SAVE_FILE_ID);
    if (btnSaveFile) {
        btnSaveFile.addEventListener('click', (e) => {
            e.preventDefault();
            const fileType = btnSaveFile.dataset.file_type;
            let body = null;
            if (fileType === FILETYPENAMES.data) {
                body = getDatasFileInfos();
            }else if (fileType === FILETYPENAMES.mapping) {
                body = getAllMappingPreviewData();
            }else if (fileType === FILETYPENAMES.importer) {
                body = getAllImporterDatas();
            }
            else {
                console.error("Type de fichier inconnu !");
                return;
            }
            if (!body) {
                console.error('Aucune donnée à envoyer !');
                return; // Assurez-vous que les données existent avant de continuer
            }
            sendToServer(body);
        });
    }

    const btnAdd = document.getElementById(BTN_ADD_FIELD_ID);
    if (btnAdd) {
        btnAdd.addEventListener('click', (e) => {
            e.preventDefault();
            const selectElement = document.getElementById(SELECT_FIELD_TO_ADD_ID);
            const listFieldContainer = document.getElementById(PREVIEW_FIELDS_CONTAINER_ID);

            if (selectElement && listFieldContainer) {
                const optionsElements = selectElement.options;
                let selectedValue = selectElement.value;

                for (let i = 0; i < optionsElements.length; i++) {
                    if (optionsElements[i].value === selectedValue && selectedValue !== "No Source") {
                        optionsElements[i].remove();
                        break;
                    }
                }
                let fixed_value = "false";
                let field_name = selectedValue;
                let unlocked = false;
                if (selectedValue === "No Source") {
                    selectedValue = null;
                    fixed_value = "true";
                    field_name = "To be defined";
                    unlocked = true;
                }

                selectElement.value = "";

                appendMappingPreviewRow({
                    source_field_name: selectedValue,
                    isfixed: fixed_value,
                    field_name: field_name,
                    type_field: 'text',
                    is_mapped: 'true',
                    analyzer: 'standard',
                    fixed_value: ''
                }, PREVIEW_FIELDS_CONTAINER_ID, unlocked);
            }
        });
    }
}

function initPreviewRowEvents(row) {
    const checkbox = row.querySelector('input[type="checkbox"][name="fixed"]');
    const sourceFieldDiv = row.querySelector('[data-field="source_field_name"]');
    const targetFieldDiv = row.querySelector('[data-field="value"]');
    const inputFields = row.querySelectorAll('select, input');
    const btnUpdate = row.querySelector('.field-picto.update');

    // verifier si fixed value est checked dans les mappings
    if (checkbox && sourceFieldDiv && targetFieldDiv) {
        checkbox.addEventListener('change', () => {
            if (checkbox.checked) {
                sourceFieldDiv.classList.add('disabled');
                targetFieldDiv.classList.remove('disabled');
            } else {
                sourceFieldDiv.classList.remove('disabled');
                targetFieldDiv.classList.add('disabled');
            }
        });

        if (checkbox.checked) {
            sourceFieldDiv.classList.add('disabled');
        }
    }

    checkRowForChanges(); // Important : vérifier l’état après changement

    function checkRowForChanges() {
        let anyChanged = false;

        inputFields.forEach(input => {
            const currentValue = input.type === 'checkbox'
                ? (input.checked ? "True" : "False")
                : input.value;

            const initialValue = input.getAttribute('data-original');

            if (currentValue !== initialValue) {
                input.classList.add('changed');
                anyChanged = true;
            } else {
                input.classList.remove('changed');
            }
        });

        if (btnUpdate) {
            btnUpdate.classList.toggle('hidden', !anyChanged);
        }
    }

    // Attacher l’écouteur à tous les inputs
    inputFields.forEach(input => {
        input.addEventListener('input', checkRowForChanges);
        if (input.type === 'checkbox') {
            input.addEventListener('change', checkRowForChanges); // Pour être sûr
        }
    });

    // Vérifie dès l'init au cas où des champs soient déjà modifiés
    checkRowForChanges();
}

function appendMappingPreviewRow(params, containerId, unlocked = false) {
    const url = new URL('/mapping-preview-row', window.location.origin);
    Object.keys(params).forEach(key => url.searchParams.append(key, params[key]));

    fetch(url)
        .then(response => {
            if (!response.ok) throw new Error('Erreur lors de la requête');
            return response.text();
        })
        .then(html => {
            const container = document.querySelector(containerId);
            const tempDiv = document.createElement('div');
            tempDiv.innerHTML = html;
            const newChild = tempDiv.firstElementChild;
            container.appendChild(newChild);
            if (unlocked === true) {
                let fixed_elem = newChild.querySelector('.fixed-value.disabled');
                if (fixed_elem) {
                    fixed_elem.classList.remove('disabled');
                }
            }

            // Appliquer les events uniquement à la nouvelle ligne
            initPreviewRowEvents(newChild);
        })
        .catch(error => {
            console.error('Erreur fetch :', error);
        });
}

function getAllFieldDatas() {
    let selector = '#'+PREVIEW_FIELDS_CONTAINER_ID + ' .field-preview';
    return document.querySelectorAll(selector);
}

function getBaseInfos() {
    const btnSaveFile = document.getElementById(BTN_SAVE_FILE_ID);
    if (!btnSaveFile) return null; // Assurez-vous que le bouton existe avant de l'utiliser
    const file_id = btnSaveFile.dataset.id;
    const filename = btnSaveFile.dataset.filename;
    const fileType = btnSaveFile.dataset.file_type;
    
    return {
        file_id: file_id,
        filename: filename,
        type_file: fileType
    };
}


function getDatasFileInfos() {
  let baseInfos = getBaseInfos();
  let datas = {}
  const container = document.getElementById(PREVIEW_CONTAINER_ID);
  if (!container) return null; // Assurez-vous que le conteneur existe avant de l'utiliser
  datas["front_name"]= container.querySelector('.filename')?.textContent.trim() || '';
  datas["separator"] = container.querySelector('.sub-sep span')?.textContent.trim() || '';

  baseInfos['datas'] = datas;
  return baseInfos;
}

function getAllMappingPreviewData() {
    let baseInfos = getBaseInfos();
    if (!baseInfos) return null; // Assurez-vous que les données de base existent avant de continuer
    const rows = getAllFieldDatas();
    let datas = [];

    rows.forEach(row => {
        const sourceField = row.querySelector('[data-field="source_field_name"]')?.textContent.trim();
        const fixedCheckbox = row.querySelector('input[type="checkbox"][name="fixed"]');
        const mappedFieldInput = row.querySelector('[data-field="mapped_field_name"] input');
        const typeFieldSelect = row.querySelector('[data-field="type_field"] select');
        const mappedSelect = row.querySelector('[data-field="mapped"] select');
        const analyzerSelect = row.querySelector('[data-field="analyzer"] select');
        const fixedValueInput = row.querySelector('[data-field="value"] input');

        const rowData = {
        source_field_name: sourceField,
        fixed: fixedCheckbox?.checked || false,
        mapped_field_name: mappedFieldInput?.value || "",
        type_field: typeFieldSelect?.value || "",
        mapped: mappedSelect?.value === "True",
        analyzer: analyzerSelect?.value || "",
        fixed_value: fixedValueInput?.value || ""
        };
    
        datas.push(rowData);
    });

    baseInfos['datas'] = datas;
    return baseInfos;
}

function getAllImporterDatas() {
    const baseInfos = getBaseInfos();
    if (!baseInfos) return null; // Assurez-vous que les données de base existent avant de continuer
    let datas = {}

    const rows = getAllFieldDatas();

    if (!rows || rows.length === 0) {
        return null; // Retourne un tableau vide si aucune ligne n'est trouvée
    }
    let datasBrutes = rows[0]
    datas['datas_filename'] = datasBrutes.querySelector('[data-field="datas_filename"]')?.textContent.trim();
    datas['datas_separator'] = datasBrutes.querySelector('[data-field="datas_separator"]')?.textContent.trim();
    datas['mappings_filename'] = datasBrutes.querySelector('[data-field="mapping_filename"]')?.textContent.trim();
    datas['index_name'] = datasBrutes.querySelector('[data-field="index_name"]')?.textContent.trim();

    baseInfos['datas'] = datas;

    return baseInfos; // Retourne le tableau de données
}

function sendToServer(body) {
    
    if (!body) {
        console.error('Aucune donnée à envoyer !');
        return; // Assurez-vous que les données existent avant de continuer
    }

    fetch('/file/save', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(body)
    }).then(response => {
        return response.json();
    }).then(result => {
        console.log('Réponse serveur :', result);
    }).catch(error => {
        console.error('Erreur fetch :', error);
    });
}


function deleteFile(filename, file_id, fileType, listFileContainer){
    const urlFileList = `/files-list/${fileType}`;
    const listFilesItems = document.querySelectorAll('.list-files');
    const item = Array.from(listFilesItems).find(item => item.dataset.id === file_id);
    const previewContainer = document.querySelector(`#preview-${fileType}-container`);

    if (confirm(`Supprimer le fichier ${filename} ?`)) {
        fetch('/file/delete', {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ file_id: file_id, filename: filename })
        })
        .then(res => {
            if (res.ok) {
                // Supprimer l'élément de la liste
                if (item){
                    item.remove();
                }
                if (previewContainer) {
                    previewContainer.innerHTML = '';
                }
                fetch(urlFileList, { headers: { "X-Requested-With": "XMLHttpRequest" } })
                    .then(response => response.text())
                    .then(html => {
                        if (listFileContainer) {
                            listFileContainer.innerHTML = html;
                            document.dispatchEvent(new Event("components:reinit"));
                        }
                    });
            } else {
                console.error("Erreur lors de la suppression");
            }


        })
        .catch(err => console.error("Erreur:", err));
    }
}

function get_base_dict(file_id, filename, fileType, frontname, separator=null) {
    result = {
        id: file_id,
        filename: filename,
        file_type: fileType,
        frontname: frontname,
    };
    if (separator) {
        result['separator'] = separator;
    }

    return result;
}
