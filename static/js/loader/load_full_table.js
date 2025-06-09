export async function fetchTableDatasByFilePath(encodedFilepath, chunkIndex) {
    if (!encodedFilepath) return false;

    const url = `/file/preview-table-path/${encodedFilepath}/${chunkIndex}`;
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
        console.error(error);
        return null;
    }
}