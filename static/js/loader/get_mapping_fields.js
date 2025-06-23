export async function queryNewMappingField(fieldInfos) {
    const url = "/mapping/create/mapping-field";
    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(fieldInfos),
        });

        if (!response.ok) {
            console.error("Erreur HTTP lors de l'ajout de mapping field", response.status);
            return false;
        }

        // On récupère le JSON
        const data = await response.json();

        if (data.error) {
            console.error("Erreur applicative:", data.error);
            return false;
        }

        // Renvoie un objet avec les deux HTML
        return {
            row_html: data.row_html,
            details_html: data.details_html
        };
    } catch (e) {
        console.error("Exception lors de l'ajout de mapping field", e);
        return false;
    }
}
