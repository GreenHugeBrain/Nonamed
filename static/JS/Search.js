const searchInput = document.querySelector('.search-input');
const submitButton = document.querySelector('.submit-input');

submitButton.addEventListener('click', () => {
    const query = searchInput.value.trim();

    if (query) {
        window.location.href = `/search/` + query;
    }

    
    
});


