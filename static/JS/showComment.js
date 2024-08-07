document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.toggle-comments').forEach(function(element) {
        element.addEventListener('click', function() {
            var container = this.nextElementSibling;
            if (container.classList.contains('active')) {
                container.classList.remove('active');
            } else {
                container.classList.add('active');
            }
        });
    });
});
