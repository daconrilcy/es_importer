export function tranformHtmlToData(rawHtml, table, inject_header=true) {
    
    const tempTable = document.createElement('table');

    tempTable.innerHTML = rawHtml;

    const newTheader = tempTable.querySelector('thead');
    const tHeader = table.querySelector('thead');

    const newTbody = tempTable.querySelector('tbody');
    const tBody = table.querySelector('tbody');

    if (inject_header== true && newTheader &&tHeader){
        tHeader.innerHTML = newTheader.innerHTML;
    }

    if (tBody && newTbody) {
        tBody.innerHTML = newTbody.innerHTML;
    }
}