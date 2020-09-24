function filePrev() {
    let file = document.getElementById("image").files[0];

    let reader = new FileReader();
    reader.onload = (event) => {
        let image = new Image();
        image.style.height = "50px";
        image.src = event.target.result;
        document.getElementById("img-prev").appendChild(image);
    }
    reader.readAsDataURL(file);
}

function selectFile() {
    let file = document.getElementById("image");
    file.click();
}

function createFileUploadObject() {
    let fileInput = document.createElement("INPUT");
    fileInput.type = "file";
    fileInput.id = "image";
    fileInput.name = "image";
    fileInput.accept = "image/*";

}