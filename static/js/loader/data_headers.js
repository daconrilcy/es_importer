export async function QueryFileDataHeaders(encodedFilepath, catField) {
    if (!encodedFilepath) return null; // cohérent de retourner null si input absent

    const CATEGORIES_FIELDS = ["source", "remplacement", "phonetic", "fixed_value"];

    if (!CATEGORIES_FIELDS.includes(catField)) return null;

    let url = `/file/mapping/undertitle/${catField}/${encodedFilepath}`;
    if (catField == "fixed_value"){
        url = `/file/mapping/undertitle/${catField}`;
    }
    try {
        const response = await fetch(url, {
            method: 'GET',
            headers: {
                'Accept': 'text/html'
            }
        });

        if (!response.ok) {
            throw new Error('Erreur lors de la récupération des données');
        }

        const html = await response.text();
        return html;

    } catch (error) {
        console.error("getFileDataHeaders:", error);
        return null;
    }
}
