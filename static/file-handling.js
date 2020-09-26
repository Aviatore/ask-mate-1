let files = []

function modifyForm() {
    let form = document.getElementById("form");
    form.addEventListener("submit", (event) => {
        event.preventDefault();
        event.target.files = files;
        event.target.submit();
    });
}

function filePrev() {
    let formFiles = document.getElementById("image").files;

    for (let file of formFiles) {
        let reader = new FileReader();

        reader.onload = (event) => {
            let image = new Image();
            image.style.height = "50px";
            image.src = event.target.result;
            document.getElementById("img-prev").appendChild(image);
        }

        reader.readAsDataURL(file);
    }
}

function selectFile() {
    let file = document.getElementById("image");

    let imageContainer = document.getElementById("img-prev");
    let images = imageContainer.querySelectorAll("img");

    for (let image of images) {
        image.parentNode.removeChild(image);
    }

    file.click();
}

window.onload = modifyForm;