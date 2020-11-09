var root = document.documentElement;

var widthConfirmed = document.getElementById("rcorners2").getAttribute("data-value"); 
var widthRejected = document.getElementById("rcorners3").getAttribute("data-value"); 
root.style.setProperty('--widthConfirmed', widthConfirmed);
root.style.setProperty('--widthRejected', widthRejected);

document.addEventListener('keyup', (event) => {
    if (event.key == 'ArrowLeft') {
        document.getElementById("back").click();

    }
    else if (event.key == 'ArrowRight') {
        document.getElementById("forward").click();

    }
    else if (event.key == 'ArrowUp') {
        document.getElementById("Landscape").click();

    }
    else if (event.key == 'ArrowDown') {
        document.getElementById("NoLandscape").click();

    }
    else if (event.key == '1') {
        document.getElementById("NonExciting").click();

    }
    else if (event.key == '2') {
        document.getElementById("Exciting").click();

    }  
    else if (event.key == '4') {
        document.getElementById("goToUnclassified").click();

    }
    });

