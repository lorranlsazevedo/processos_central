import csv
import os
import django

# Configura o Django para usar as configurações do projeto
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'central_de_processos.settings')  # Certifique-se de que o nome do projeto está correto
django.setup()

from extracao_pdf.models import Cidade, Estado  # Ajuste o nome do app conforme necessário

# Mapeamento de Código IBGE para ID do Estado no Sistema
estado_mapping = {
    11: 23, 12: 1, 13: 7, 14: 20, 15: 17, 16: 6,
    17: 27, 21: 13, 22: 19, 23: 9, 24: 21, 25: 18,
    26: 19, 27: 2, 28: 26, 29: 8, 31: 16, 32: 11,
    33: 5, 35: 4, 41: 3, 42: 25, 43: 22, 50: 15,
    51: 14, 52: 12, 53: 10
}

# Caminho para o arquivo CSV
csv_path = r'C:\Users\lorra\Downloads\cidades.csv'

try:
    with open(csv_path, encoding='ISO-8859-1') as csvfile:  # Tente com encoding='ISO-8859-1' ou outro compatível
        reader = csv.DictReader(csvfile)
        for row in reader:
            codigo_ibge = int(row['UF'])  # Código da UF na planilha
            estado_id = estado_mapping.get(codigo_ibge)
            if estado_id:
                estado = Estado.objects.get(id=estado_id)
                Cidade.objects.create(
                    nome=row['Nome_Município'],
                    estado=estado,
                    comarca=False  # Ajuste conforme necessário
                )
            else:
                print(f"Estado com código {codigo_ibge} não encontrado no mapeamento.")
except UnicodeDecodeError as e:
    print(f"Erro de decodificação: {e}")
