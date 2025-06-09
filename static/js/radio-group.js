// radio-group.js

/**
 * Gère le comportement exclusif des groupes de boutons radio stylisés.
 */
export function initRadioGroups() {
    document.querySelectorAll('.btn-group.radio-behavior').forEach(group => {
        const buttons = group.querySelectorAll('button');
        buttons.forEach(btn => {
            btn.addEventListener('click', function () {
                buttons.forEach(b => b.classList.remove('active'));
                this.classList.add('active');
            });
        });
    });
}
