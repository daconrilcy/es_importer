export async function injectGetPhoneticToFile(phoneticToInject, filepath, field, sep) {
    const url = "/file/add/phonetic/";
    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ filepath, sep, column: field, phonetic: phoneticToInject }),
        });

        if (!response.ok) {
            console.error("Erreur HTTP lors de l'ajout de phonétique", response.status);
            return false;
        }

        const data = await response.json();
        if (data.success) {
            return data;
        } else {
            console.error("Erreur applicative lors de l'ajout de phonétique", data.error);
            return false;
        }
    } catch (e) {
        console.error("Exception lors de l'ajout de phonétique", e);
        return false;
    }
}

