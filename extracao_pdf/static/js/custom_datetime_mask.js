$(document).ready(function () {
    // Aplica a máscara para campos com a classe date-mask
    $('.date-mask').mask('00/00/0000', {
        placeholder: "dd/mm/aaaa"
    });
    // Aplica a máscara para campos com a classe hour-mask
    $('.hour-mask').mask('00:00', {
        placeholder: "hh:mm"
    });
});
