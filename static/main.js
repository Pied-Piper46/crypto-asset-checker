window.onload = function() {
    var cells = document.getElementsByClassName('colorValue');

    for (var i = 0; i < cells.length; i++) {
        var value = parseFloat(cells[i].innerText);

        if (value < 0.0) {
            cells[i].style.color = '#FF5722';
        } else if (value > 0.0) {
            cells[i].innerText = "+" + cells[i].innerText;
            cells[i].style.color = '#37AB9D';
        } else {
            continue;
        }
    }

}