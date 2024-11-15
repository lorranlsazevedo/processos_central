import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io
import re
from notifications.signals import notify
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from extracao_pdf.models import Processo
from django.utils.timezone import now, localtime, make_naive


pytesseract.pytesseract.tesseract_cmd = r'D:\Program Files\Tesseract-OCR\tesseract.exe'


def aplicar_ocr_na_imagem(pixmap):
    imagem = Image.open(io.BytesIO(pixmap.tobytes()))
    texto = pytesseract.image_to_string(imagem, lang='por')  # Supondo que o documento é em português
    return texto


def extrair_texto_com_orientacao(arquivo_pdf):
    documento = fitz.open(stream=arquivo_pdf.read(), filetype="pdf")
    texto_por_pagina = []

    for pagina in documento:
        texto_pagina = ''
        blocos = pagina.get_text("dict")["blocks"]
        conta_texto = 0  # Contador para o texto extraído

        for bloco in blocos:
            if 'lines' in bloco:
                for linha in bloco['lines']:
                    for span in linha['spans']:
                        rotation = span.get('rotation', 0)
                        if -15 <= rotation <= 15:
                            texto_pagina += span['text'] + ' '
                            conta_texto += len(span['text'])

        # Se a quantidade de texto for baixa, considera a possibilidade de ser uma página escaneada e aplica OCR
        if conta_texto < 500:  # O limiar pode precisar de ajustes
            try:
                pix = pagina.get_pixmap()
                texto_pagina += aplicar_ocr_na_imagem(pix)
            except Exception as e:
                print(f"Erro ao aplicar OCR na página {pagina.number}: {e}")

        texto_por_pagina.append(texto_pagina)

    documento.close()
    return texto_por_pagina


def encontrar_numero_processo(texto):
    padrao_processo = r'\d{7}-\d{2}.\d{4}.\d.\d{2}.\d{4}'
    resultados = re.findall(padrao_processo, texto)
    return max(set(resultados), key = resultados.count) if resultados else None


def enviar_notificacao(remetente, destinatario, mensagem):
    notify.send(remetente, recipient=destinatario, verb=mensagem)

def get_filtered_processos(request):
    filtros = {}
    estado = request.GET.get('estado')
    leiloeiro = request.GET.get('leiloeiro')
    dias_antes_leilao = request.GET.get('dias_antes_leilao')
    dias_depois_cadastro = request.GET.get('dias_depois_cadastro')
    intervalo_inicio = request.GET.get('intervalo_inicio')
    intervalo_fim = request.GET.get('intervalo_fim')
    coluna_kanban = request.GET.get('coluna_kanban')  # Filtro de coluna Kanban

    hoje = localtime(now()).date()

    # Aplicar filtros
    if estado:
        filtros['vara__comarca__estado__nome'] = estado
    if leiloeiro:
        filtros['leiloeiro__nome'] = leiloeiro

    # Filtro para leilões com datas futuras
    processos = Processo.objects.filter(**filtros).exclude(
        leilao__datas_leilao__data_hora__lt=now()
    ).distinct()

    # Aplicar filtro de coluna Kanban via Card
    if coluna_kanban:
        # Obter processos que têm um Card relacionado à coluna Kanban especificada
        processos = processos.filter(card__list_id=coluna_kanban)

    # Log para verificar os filtros aplicados
    print(f"Filtros aplicados: {filtros}")

    # Consolidar as datas dos leilões para encontrar a primeira e a última
    processos_consolidados = []
    for processo in processos:
        datas_leilao = list(processo.leilao.datas_leilao.order_by('data_hora').values_list('data_hora', flat=True))
        if datas_leilao:
            processo.primeira_data = make_naive(datas_leilao[0]).strftime('%d/%m/%Y %H:%M')
            processo.ultima_data = make_naive(datas_leilao[-1]).strftime('%d/%m/%Y %H:%M') if len(datas_leilao) > 1 else processo.primeira_data
        else:
            processo.primeira_data = 'N/A'
            processo.ultima_data = 'N/A'
        processos_consolidados.append(processo)

    # Aplicar filtros adicionais conforme necessário
    if dias_antes_leilao:
        dias_antes_leilao = int(dias_antes_leilao)
        data_limite = hoje + timedelta(days=dias_antes_leilao)
        processos_consolidados = [
            processo for processo in processos_consolidados
            if processo.primeira_data and hoje <= datetime.strptime(processo.primeira_data, '%d/%m/%Y %H:%M').date() <= data_limite
        ]

    if dias_depois_cadastro:
        dias_depois_cadastro = int(dias_depois_cadastro)
        processos_consolidados = [
            processo for processo in processos_consolidados
            if processo.data_cadastro and hoje - timedelta(days=dias_depois_cadastro) <= processo.data_cadastro <= hoje
        ]

    if intervalo_inicio and intervalo_fim:
        try:
            data_inicio = datetime.strptime(intervalo_inicio, '%Y-%m-%d').date()
            data_fim = datetime.strptime(intervalo_fim, '%Y-%m-%d').date()
            processos_consolidados = [
                processo for processo in processos_consolidados
                if processo.primeira_data and data_inicio <= datetime.strptime(processo.primeira_data, '%d/%m/%Y %H:%M').date() <= data_fim
            ]
        except ValueError:
            print("Erro ao converter as datas de intervalo. Verifique o formato das datas.")

    return processos_consolidados