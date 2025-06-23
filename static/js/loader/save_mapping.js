export async function querySaveMappingFile(payload){
    const url = "/file/mapping/save/";

    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
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

        // Succès : on renvoie true
        return { success: true, new_file: data.new_file};
    } catch (e) {
        console.error("Exception lors de l'appel du serveur", e);
        return { success: false, error: e.message || "Erreur réseau inconnue" };
    }

}