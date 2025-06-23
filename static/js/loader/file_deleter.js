/**
 * Supprime un fichier via l'API Flask /file/delete/.
 * 
 * @param {Object} params - Paramètres d'identification du fichier.
 * @param {string} [params.file_id] - L'identifiant du fichier à supprimer.
 * @param {string} [params.filename] - Le nom du fichier à supprimer.
 * @returns {Promise<Object>} - Le résultat de la requête.
 */
export async function queryDeleteFile({ file_id, filename }) {
    const url = '/file/delete/';
    const payload = {};
    if (file_id) payload.file_id = file_id;
    if (filename) payload.filename = filename;

    // Protection : au moins un des deux paramètres doit être fourni
    if (!payload.file_id && !payload.filename) {
        throw new Error('file_id ou filename doit être renseigné');
    }

    const response = await fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            // 'Authorization': 'Bearer token', // si besoin
        },
        body: JSON.stringify(payload)
    });

    const data = await response.json();
    if (!response.ok) {
        // Gestion de l’erreur côté client
        throw new Error(data.error || 'Erreur inconnue');
    }
    return data;
}
