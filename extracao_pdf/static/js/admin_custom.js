document.addEventListener('DOMContentLoaded', function() {
  const estadoSelect = document.getElementById('id_estado');
  const cidadeSelect = document.getElementById('id_cidade');

  estadoSelect.addEventListener('change', function() {
    const estadoId = this.value;
    fetch(`/cidades/${estadoId}/`) // Substitua com a URL que retorna as cidades para o estado
      .then(response => response.json())
      .then(data => {
        cidadeSelect.innerHTML = ''; // Limpa as cidades anteriores
        data.forEach(cidade => {
          const option = new Option(cidade.nome, cidade.id);
          cidadeSelect.add(option);
        });
      })
      .catch(error => console.error('Erro ao buscar cidades:', error));
  });
});

$(document).ready(function(){
    $('.currency-input').mask('#.##0,00', {reverse: true});
});