function debounce(func, wait) {
    let timeout;

    return function executedFunction(...args) {
        const later = function() {
            clearTimeout(timeout);
            func(...args);
        };

        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
};

document.addEventListener('DOMContentLoaded', function () {
    const searchFields = document.querySelectorAll('.autocomplete-input');

    searchFields.forEach(function (field) {
        // Certifique-se de substituir 'eventKeyupHandler' pela lógica que você deseja debouncar
        field.addEventListener('keyup', debounce(function (event) {
            // A função que você quer debouncar, provavelmente uma chamada AJAX para a pesquisa.
        }, 250));  // Aguarda 250 ms após o usuário parar de digitar
    });
});
