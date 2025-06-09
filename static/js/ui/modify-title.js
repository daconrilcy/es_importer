export function initModifyTitle() {
    const modifyButtonsContainer = document.querySelectorAll('.modify-buttons')[0];
    if (!modifyButtonsContainer) return;
    const modifyButtons = modifyButtonsContainer.querySelectorAll('.glyphicon');
    modifyButtons.forEach(button => {
        if (button.classList.contains('glyphicon-modify')) {
            button.addEventListener('click', clickModifyButton);
        }
        if (button.classList.contains('glyphicon-modify-accept')) {
            button.addEventListener('click', clickAcceptButton);
        }
        if (button.classList.contains('glyphicon-modify-revert')) {
            button.addEventListener('click', clickRevertButton);
        }
    });


    function clickModifyButton() {
        const fileTitleContainer = document.querySelector('.page-title');
        if (!fileTitleContainer) return;
        const input = fileTitleContainer.querySelector('input');
        if (!input) return;
        toggleModifyButtons();
        input.classList.toggle('modify');
    }

    function toggleModifyButtons() {
        const modifyButtons = document.querySelectorAll('.modify-buttons .glyphicon');
        if (!modifyButtons) return;
        modifyButtons.forEach(button => {
            button.classList.toggle('visible');
        });
    }

    function clickAcceptButton() {
        sendTitleUpdate();
    }

    function clickRevertButton() {
        const fileTitleContainer = document.querySelector('.page-title');
        if (!fileTitleContainer) return;
        const input = fileTitleContainer.querySelector('input');
        if (!input) return;
        const originalValue = input.getAttribute('data-original-value');
        if (!originalValue) return;
        input.classList.remove('modify');
        toggleModifyButtons();
        input.value = originalValue;
    }

    function sendTitleUpdate() {
        const fileTitleContainer = document.querySelector('.page-title');
        if (!fileTitleContainer) return;
        const input = fileTitleContainer.querySelector('input');
        if (!input) return;
        const frontName = input.value;
        const fileId = input.getAttribute('data-file-id');
        if (!fileId) return;
        fetch('/file/update_front_name', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ front_name: frontName, file_id: fileId }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                input.classList.remove('modify');
                toggleModifyButtons();
            } else {
                console.error('Erreur lors de la mise à jour du nom de fichier:', data.error);
            }
        })
        .catch(error => {
            console.error('Erreur lors de la mise à jour du nom de fichier:', error);
        });
    }
}
