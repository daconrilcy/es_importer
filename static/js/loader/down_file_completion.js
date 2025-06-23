const MAPPIMG_FIELD_URL_REMPLACEMENT_FILE_DOWNLOAD_LINK = "/file/remplacement/download/";

export function downloadCompletion(filename){
    const url = `${MAPPIMG_FIELD_URL_REMPLACEMENT_FILE_DOWNLOAD_LINK}${encodeURIComponent(filename)}`;
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}
