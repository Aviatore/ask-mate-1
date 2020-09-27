const MAX_SIZE = 512 * 1024;
let tooLarge = false;

function sizeConverter(size) {
    return (size < 1000 ? size.toString() + " b" : (size / 1000).toFixed(1).toString() + " kb" );
}

function modifyForm() {
    let form = document.getElementById("form");
    form.addEventListener("submit", (event) => {
        event.preventDefault();

        if (tooLarge) {
            alert("One of selected files is too large.\nPlease select a new file(s).");
        }
        else {
            event.target.submit();
        }
    });
}

function filePrev() {
    tooLarge = false;
    let formFiles = document.getElementById("image").files;

    for (let file of formFiles) {
        let fileIsTooLarge = false;

        if (file.size > MAX_SIZE) {
            console.log(file.size);
            if (!tooLarge) {
                let warningSpan = document.createElement("span");
                warningSpan.classList.add("text-warning");
                warningSpan.classList.add("center");
                warningSpan.classList.add("image-warning");
                warningSpan.innerHTML = "The selected file(s) is larger than " + sizeConverter(MAX_SIZE);
                document.getElementById("input-file-container").appendChild(warningSpan);
                tooLarge = true;
            }
            fileIsTooLarge = true;
        }

        let reader = new FileReader();

        reader.onload = (event) => {
            let image = new Image();
            image.style.height = "50px";

            if (fileIsTooLarge) {
                image.style.border = "2px solid red";
            }

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
    let warnings = document.getElementsByClassName("image-warning");

    for (let image of images) {
        image.parentNode.removeChild(image);
    }

    for (let warning of warnings) {
        warning.parentNode.removeChild(warning);
    }

    file.click();
}

window.onload = modifyForm;