import { LIST_FILE_CONTAINER_ID, PREVIEW_CONTAINER_ID } from "./config.js";

export function initFileRowEvents() {
    const listFilesItems = document.querySelectorAll('.list-files');
    if (listFilesItems.length === 0) {
        return;
    }
    listFilesItems.forEach(item => {
        const updateBtn = item.querySelector(".btn-update");
        const deleteBtn = item.querySelector(".btn-delete");
        const separatorInput = item.querySelector(".separator-input");
        const fileNameInput = item.querySelector(".file-name");


        // Preview on click
        item.addEventListener("click", (e) => handlePreviewClick(e, item));

        // Update btn
        if (updateBtn) {
            updateBtn.addEventListener("click", (e) => handleUpdateClick(e, item));
        }

        // Delete btn
        if (deleteBtn) {
            deleteBtn.addEventListener("click", (e) => handleDeleteClick(e, item));
        }

        // Show update btn on input
        if (separatorInput) {
            separatorInput.addEventListener("input", (e) => {
                handleSeparatorChange(e);
            });
        }
        if (fileNameInput) {
            fileNameInput.addEventListener("input", () => {
                updateBtn.classList.remove("hidden");
            });
        }
    });
}

function handlePreviewClick(event, item) {
    // Ne pas déclencher si clic sur bouton
    event.stopPropagation();
    const listFilesItems = document.querySelectorAll('.list-files');
    if (listFilesItems.length === 0) {
        return;
    }
    if (event.target.closest(".btn-update") || event.target.closest(".btn-delete")) return;

    const id_file = item.dataset.id;
    const status = item.getAttribute("data-status");
    listFilesItems.forEach((el) => {
        el.classList.remove("active");
    });

    if (status == "missing") {
        alert("Le fichier n'est pas disponible");
        return;
    }
    item.classList.toggle("active");

    loadFilePreview(id_file);
}

function handleUpdateClick(event, item) {
    event.stopPropagation();
    const inputSep = item.querySelector(".separator-input");
    const inputFilename = item.querySelector(".file-name");
    const id_file = item.dataset.id;
    const filename = inputFilename.value;
    const separator = inputSep.value;
    const fileType = item.dataset.filetype;

    updateFile(filename, separator, fileType, id_file, item.querySelector(".update-btn"));
}

function handleDeleteClick(event, item) {
    event.stopPropagation();
    const listFileContainer = document.getElementById(LIST_FILE_CONTAINER_ID);
    const filename = item.dataset.filename;
    const file_id = item.dataset.id;
    const fileType = item.dataset.filetype;
    const urlFileList = `/files-list/${fileType}`;

    if (confirm(`Supprimer le fichier ${filename} ?`)) {
        fetch(`/delete`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ file_id: file_id, filename: filename })
        })
        .then(res => {
            if (res.ok) {
                item.remove();
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


function loadFilePreview(file_id) {
    const url = `/file-preview/${file_id}`;
    fetch(url)
        .then(response => {
            if (!response.ok) {
                throw new Error(`Erreur serveur (${response.status})`);
            }
            return response.text();
        })
        .then(html => {
            document.getElementById(PREVIEW_CONTAINER_ID).innerHTML = html;
            document.dispatchEvent(new Event("preview:reinit"));
        })
        .catch(error => {
            console.error("Erreur lors du chargement :", error);
            document.getElementById(PREVIEW_CONTAINER_ID).innerHTML
            = `<div class="alert alert-danger">${error.message}</div>`;
        });
}


function updateFile(filename, separator, fileType, id_file, button) {

    if (fileType == "datas") {
        updateFileDatas(filename, separator, id_file, button);
    } else {
        console.error("Type de fichier non géré");
    }
}

function updateFileDatas(filename, separator,id_file, button) {
    const body_value = JSON.stringify({ id_file, filename, separator });
    console.log(body_value);
    fetch(`/modify/datas`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: body_value
    })
        .then(res => {
            if (res.ok) {
                button.classList.add("hidden");
                console.log("Mise à jour effectuée");
            } else {
                alert("Erreur lors de la mise à jour");
            }
        })
        .catch(err => console.error("Erreur:", err));
}

function handleSeparatorChange(event) {
    const inputSep = event.target;
    const value = inputSep.value;

    const btnUpdate = inputSep.closest('.list-files').querySelector('.btn-update');
    if (btnUpdate === null) {
        return;
    }
    const initialeValue = inputSep.getAttribute('data-original');
    if (value === initialeValue) {
        btnUpdate.classList.add('hidden');
        return;
    }
    if (value) {
        btnUpdate.classList.remove('hidden');
    } else {
        btnUpdate.classList.add('hidden');
    }
}
