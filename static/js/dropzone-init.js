export function initializeDropzone() {
    Dropzone.autoDiscover = false;
    let dropzoneElement = document.querySelector("#myDropzone");

    if (!dropzoneElement || dropzoneElement.classList.contains("dz-started")) return;

    const fileExtensions = dropzoneElement.getAttribute("data-accepted-files") || ".csv";
    const urlUpload = dropzoneElement.getAttribute("data-upload-url") || "/upload";
    const fileType = dropzoneElement.getAttribute("data-filetype") || "datas";
    const listFileContainer = document.getElementById("list_files_container");
    const fileListUrl = "/files-list/"+fileType;
    new Dropzone("#myDropzone", {
        url: urlUpload,
        maxFilesize: 500,
        acceptedFiles: fileExtensions,
        addRemoveLinks: true,
        init: function () {
            this.on("sending", function(file, xhr, formData) {
                formData.append("filetype", fileType);
            });
            this.on("success", () =>{
                console.log("Fichier uploadé avec succès !");
                fetch(fileListUrl, { headers: { "X-Requested-With": "XMLHttpRequest" } })
                    .then(response => response.text())
                    .then(html => {
                        console.log("Récupération de la liste des fichiers");
                        if (listFileContainer) {
                            listFileContainer.innerHTML = html;
                        }
                        document.dispatchEvent(new Event("components:reinit"));
                    });
                });
            this.on("error", (file, errorMessage) => console.log("Erreur lors de l'upload : " + errorMessage));
        }
    });

    console.log("Dropzone correctement initialisée !");
}