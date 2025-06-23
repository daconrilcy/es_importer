export async function queryRemplacementFile(fileInfos, fileType) {
    if (!fileType){
        fileType = "remplacement";
    }
    const url = `/file/mapping/${fileType}/generate/`;

    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(fileInfos),
        });

        let data;
        try {
            data = await response.json();
        } catch {
            // Réponse non JSON (ex: 500 côté serveur sans JSON)
            console.error("Réponse du serveur non JSON");
            return { success: false, error: "Réponse du serveur non lisible" };
        }

        if (!response.ok) {
            // Si le serveur a retourné une erreur explicite
            return { success: false, error: data?.error || "Erreur HTTP", status: response.status };
        }

        if (data.error) {
            // Cas rare : erreur applicative dans le JSON malgré un statut HTTP 200
            return { success: false, error: data.error };
        }

        // Succès : on renvoie le nom du fichier
        return data.filename;
    } catch (e) {
        console.error("Exception lors de l'appel du serveur", e);
        return { success: false, error: e.message || "Erreur réseau inconnue" };
    }
}
