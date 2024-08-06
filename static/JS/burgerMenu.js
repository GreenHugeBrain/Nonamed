let burgerIcon = document.getElementById('menu');
let burgerMenu = document.querySelector('.burgerMenu');

burgerIcon.addEventListener('click', function() {
    if (burgerMenu.style.display === 'grid') {
        burgerMenu.style.display = 'none';
    } else {
        burgerMenu.style.display = 'grid';
    }
});
