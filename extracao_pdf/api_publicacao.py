import requests
import logging
from django.utils import timezone
from datetime import timedelta
import pytz
from django.utils.timezone import localtime
import os
from django.conf import settings
from bs4 import BeautifulSoup
from extracao_pdf.models import ProcessoArquivo, CardsAgregados, Card

logger = logging.getLogger(__name__)


def publicar_edital(card):
    try:
        brasil_timezone = pytz.timezone('America/Sao_Paulo')

        session = requests.Session()
        login_url = "http://192.168.0.9/dev/publicjud/usuarios/login"
        login_data = {
            'data[Usuario][login]': 'lorranazevedo',
            'data[Usuario][senha]': 'kalachi01',
        }

        headers = {
            'User-Agent': 'PostmanRuntime/7.41.2',
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        }

        response = session.post(login_url, headers=headers, data=login_data)
        if "Acessar sua conta" in response.text:
            raise Exception("Falha no login. Verifique suas credenciais.")

        logger.info(f"Login bem-sucedido para o card: {card.id}")

        leilao = card.leilao
        if not leilao:
            raise Exception("Leilão não encontrado para o card.")

        datas_leilao = leilao.datas_leilao.all().order_by('data_hora')
        if datas_leilao.exists():
            primeira_data_leilao = localtime(datas_leilao.first().data_hora, brasil_timezone).strftime(
                '%d/%m/%Y %H:%M:%S')
            ultima_data_leilao = localtime(datas_leilao.last().data_hora, brasil_timezone).strftime('%d/%m/%Y %H:%M:%S')
        else:
            raise Exception("Nenhuma data de leilão encontrada para o card.")

        cidade_nome = card.vara.comarca.nome if card.vara and card.vara.comarca else 'N/A'
        estado_uf = card.vara.comarca.estado.uf if card.vara and card.vara.comarca and card.vara.comarca.estado else 'N/A'

        link_lote = card.leiloeiro.site if card.leiloeiro and card.leiloeiro.site else 'N/A'

        modalidade_mapping = {
            'presencial': '1',
            'eletronico': '2',
            'misto': '3'
        }
        modalidade = modalidade_mapping.get(leilao.modalidade, '1')

        data = {
            #'data[Diario][nome]': f'Teste de Leilão {card.id}',
            'data[Diario][justica]': card.vara.justica.nome if card.vara and card.vara.justica else 'N/A',
            'data[Diario][vara]': card.vara.nome if card.vara else 'N/A',
            'data[Diario][cidade_nome]': cidade_nome,
            'data[Diario][estado_uf]': estado_uf,
            'data[Diario][data_primeiro_leilao]': primeira_data_leilao,
            'data[Diario][data_ultimo_leilao]': ultima_data_leilao,
            'data[Diario][data_disponibilizacao]': localtime(timezone.now(), brasil_timezone).strftime('%d/%m/%Y'),
            'data[Diario][modalidade]': modalidade,
            'data[Diario][link_lote]': link_lote,
            'data[Diario][tipobens][1]': '1',  # Automóveis
            'data[Diario][tipobens][2]': '0',  # Imóveis
            'data[Diario][tipobens][3]': '1',  # Móveis
            'data[Diario][tipobens][4]': '0',  # Máquinas
            'data[Diario][tipobens][6]': '0',  # Náutica
            'data[Diario][conteudo]': card.description,
            'data[Diario][api]': '1',
        }

        processos_agregados = CardsAgregados.objects.filter(card=card).select_related('processo')
        if not processos_agregados.exists():
            raise Exception("Nenhum processo agregado encontrado para o card.")

        files = {}
        index = 0
        opened_files = []
        for processo_agregado in processos_agregados:
            processo = processo_agregado.processo
            anexos = ProcessoArquivo.objects.filter(processo=processo, tipo_anexo_id=2)
            for anexo in anexos:
                file_path = os.path.join(settings.MEDIA_ROOT, anexo.arquivo.name)
                if os.path.exists(file_path):
                    file_obj = open(file_path, 'rb')
                    files[f'data[Anexo][{index}][arquivo]'] = (anexo.nome_arquivo, file_obj, 'application/pdf')
                    opened_files.append(file_obj)
                    index += 1
                else:
                    logger.warning(f"Arquivo {file_path} não encontrado.")

        logger.info(f"Arquivos anexos preparados para o card {card.id}: {files}")

        api_url = "http://192.168.0.9/dev/publicjud/diarios/publicarEdital"
        response = session.post(api_url, headers=headers, data=data, files=files)

        response_text = response.text

        logger.info(f"Resposta da publicação do edital para o card {card.id}: {response.status_code}, {response_text}")

        for file_obj in opened_files:
            file_obj.close()

        if response.status_code != 200:
            raise Exception(f"Erro na publicação do edital: {response_text}")

        soup = BeautifulSoup(response_text, 'html.parser')
        diario_id_div = soup.find('div', {'id': 'diario-id'})
        if diario_id_div:
            diario_id = diario_id_div.text.strip()
            publicjud_url = f"http://192.168.0.9/dev/publicjud/diarios/{diario_id}"

            Card.objects.filter(pk=card.pk).update(identificador_publicjud=publicjud_url, publicado=True)

            logger.info(f"Identificador PUBLICJUD salvo para o card {card.id}: {publicjud_url}")
        else:
            logger.warning(f"ID do diário não encontrado na resposta para o card {card.id}.")

        return response_text

    except Exception as e:
        logger.error(f"Erro ao publicar edital para o card {card.id}: {e}")
        return str(e)
