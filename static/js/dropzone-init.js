export function initializeDropzone() {
    if (typeof Dropzone !== 'undefined') {
        Dropzone.autoDiscover = false;
    }

    const filetypeSwitchGroup = document.getElementById('filetype-switch-group');
    if (!filetypeSwitchGroup) {
        // Les boutons ne sont pas encore dans le DOM, on arrête ici
        return;
    }

    // Nettoyage préalable : supprimer tous les inputs cachés
    document.querySelectorAll('input.dz-hidden-input').forEach(input => input.remove());

    const dropzoneElement = document.getElementById('my-dropzone');
    if (!dropzoneElement) return;

    // Détruire l'ancienne instance Dropzone si elle existe
    if (dropzoneElement.dropzone) {
        dropzoneElement.dropzone.destroy();
        document.querySelectorAll('input.dz-hidden-input').forEach(input => input.remove());
    }

    const hiddenFiletype = document.getElementById('hidden-filetype');
    const uploadSuccess = document.getElementById('upload-success');
    const uploadError = document.getElementById('upload-error');
    const dzMainMessage = document.querySelector('.dz-main-message');
    const dzTypeFile = document.querySelector('.dz-type-file');
    const dzDefaultMessage = document.querySelector('.dz-default.dz-message');

    // --- Fonctions utilitaires ---
    function getActiveBtn() {
        return filetypeSwitchGroup.querySelector('button.active');
    }

    function getCurrentAccept() {
        const activeBtn = getActiveBtn();
        return activeBtn ? activeBtn.dataset.extensions : '.csv';
    }

    function updateHiddenInputAccept() {
        const accept = getCurrentAccept();
        document.querySelectorAll('input.dz-hidden-input').forEach(input => {
            input.setAttribute('accept', accept);
        });
    }

    function updateDropzoneLabels() {
        const activeBtn = getActiveBtn();
        if (dzMainMessage && activeBtn) {
            const nbsp = String.fromCharCode(160);
            dzMainMessage.innerHTML = `Déposez vos fichiers <span>${nbsp}${activeBtn.dataset.type}${nbsp}</span> ici pour les importer`;
        }
        if (dzTypeFile && activeBtn) {
            dzTypeFile.textContent = 'Extensions acceptées : ' + activeBtn.dataset.extensions;
        }
    }

    function updateDropzoneAcceptedFiles(dz) {
        dz.options.acceptedFiles = getCurrentAccept();
    }

    function showDropzoneSpinner() {
        if (!dropzoneElement) return;
        dropzoneElement.classList.add('dz-blur');
        // Cacher le message Dropzone
        const dzMsg = dropzoneElement.querySelector('.dz-default.dz-message');
        if (dzMsg) dzMsg.classList.add('hidden');
        let spinner = dropzoneElement.querySelector('#dz-upload-spinner');
        if (!spinner) {
            spinner = document.createElement('div');
            spinner.id = 'dz-upload-spinner';
            spinner.innerHTML = `
                <div class="dz-spinner-overlay">
                    <div class="dz-spinner"></div>
                </div>
            `;
            dropzoneElement.appendChild(spinner);
        }
        spinner.style.display = 'flex';
    }

    function hideDropzoneSpinner() {
        if (!dropzoneElement) return;
        dropzoneElement.classList.remove('dz-blur');
        const spinner = dropzoneElement.querySelector('#dz-upload-spinner');
        if (spinner) spinner.style.display = 'none';
        // Réafficher le message Dropzone si aucun fichier n'est présent
        const dzMsg = dropzoneElement.querySelector('.dz-default.dz-message');
        if (dzMsg && dropzoneElement.dropzone && dropzoneElement.dropzone.files.length === 0) {
            dzMsg.classList.remove('hidden');
        }
    }

    // --- Initialisation Dropzone ---
    const dz = new Dropzone('#my-dropzone', {
        url: '/dropzone-upload',
        paramName: 'file',
        maxFiles: 1,
        acceptedFiles: getCurrentAccept(),
        addRemoveLinks: true,
        dictRemoveFile: '<span class="glyphicon glyphicon-remove"></span>',
        init: function() {
            this.on('sending', function() {
                showDropzoneSpinner();
            });
            this.on('success', function(file) {
                hideDropzoneSpinner();
                if (uploadSuccess) uploadSuccess.style.display = 'block';
                if (uploadError) uploadError.style.display = 'none';
                if (dzDefaultMessage) dzDefaultMessage.classList.add('hidden');
            });
            this.on('error', function(file) {
                hideDropzoneSpinner();
                if (uploadSuccess) uploadSuccess.style.display = 'none';
                if (uploadError) uploadError.style.display = 'block';
                if (file.previewElement) {
                    file.previewElement.classList.add('dz-error');
                }
            });
            this.on('removedfile', function() {
                if (dzDefaultMessage && this.files.length === 0) {
                    dzDefaultMessage.classList.remove('hidden');
                }
            });
            this.on('addedfile', function(file) {
                const removeLink = file.previewElement && file.previewElement.querySelector('a.dz-remove');
                if (removeLink) {
                    removeLink.classList.add('btn', 'btn-primary');
                }

                // Personnaliser la vignette selon le type de fichier
                const img = file.previewElement && file.previewElement.querySelector('.dz-image img[data-dz-thumbnail]');
                if (img) {
                    const filename = file.name.toLowerCase();
                    if (filename.endsWith('.csv')) {
                        img.src = '/static/img/csv_picto.png';
                        img.alt = 'CSV';
                    } else if (filename.endsWith('.json')) {
                        img.src = '/static/img/json_picto.png';
                        img.alt = 'JSON';
                    } else if (filename.endsWith('.xml')) {
                        img.src = '/static/img/xml_picto.png';
                        img.alt = 'XML';
                    }
                }
            });
        },
        sending: function(file, xhr, formData) {
            const activeBtn = getActiveBtn();
            if (activeBtn) {
                formData.set('filetype', activeBtn.dataset.type);
                hiddenFiletype.value = activeBtn.dataset.type;
                updateDropzoneAcceptedFiles(this);
                updateDropzoneLabels();
                updateHiddenInputAccept();
            }
        }
    });

    // Après création, s'assurer qu'il n'y a qu'un seul input caché
    const allInputs = Array.from(document.querySelectorAll('input.dz-hidden-input'));
    if (allInputs.length > 1) {
        allInputs.slice(0, -1).forEach(input => input.remove());
    }
    updateHiddenInputAccept();

    // S'assurer qu'un bouton est actif au chargement
    if (!getActiveBtn()) {
        const firstBtn = filetypeSwitchGroup.querySelector('button');
        if (firstBtn) firstBtn.classList.add('active');
    }
    // Labels initiaux
    updateDropzoneLabels();

    // Listener unique pour le changement de type
    filetypeSwitchGroup.addEventListener('click', function(e) {
        if (e.target && e.target.matches('button')) {
            updateDropzoneLabels();
            updateDropzoneAcceptedFiles(dz);
            updateHiddenInputAccept();
        }
    });
}