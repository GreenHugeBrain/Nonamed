document.querySelectorAll('.toggle-comments').forEach(function(element) {
    element.addEventListener('click', function() {
        var container = this.nextElementSibling;
        container.classList.toggle('active');
    });
});