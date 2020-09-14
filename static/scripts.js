function thumb_toggle() {
    if (this.classList.contains('far')) {
        this.classList.remove('far');
        this.classList.add('fas');
    }
    else {
        this.classList.remove('fas');
        this.classList.add('far');
    }
}

function add_toggle() {
    let thumbs = document.querySelectorAll('i.icon')

    for (let i=0; i<thumbs.length; i++) {
        thumbs[i].addEventListener('mouseover', thumb_toggle)
    }
    for (let i=0; i<thumbs.length; i++) {
        thumbs[i].addEventListener('mouseout', thumb_toggle)
    }
}

window.onload = add_toggle;