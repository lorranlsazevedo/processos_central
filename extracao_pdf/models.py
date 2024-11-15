from django.db import models
from django.utils import timezone
timezone.now()
from django.core.validators import MinValueValidator, MaxValueValidator
from tinymce.models import HTMLField
from .validators import validate_file_extension
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
import uuid
from django.utils.deconstruct import deconstructible
import os
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.conf import settings
from django.core.validators import RegexValidator, validate_email
from localflavor.br.models import BRPostalCodeField

class ClasseProcessual(models.Model):
    PUBLICACAO_CHOICES = [
        ('Interno', 'Interno'),
        ('Externo', 'Externo'),
    ]

    nome = models.CharField(max_length=255)
    publicacao = models.CharField(max_length=7, choices=PUBLICACAO_CHOICES, default='Interno')

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = 'Classe processual'
        verbose_name_plural = 'Classes processuais'


class Estado(models.Model):
    nome = models.CharField(max_length=100, verbose_name='Nome do Estado')
    uf = models.CharField(max_length=2, unique=True, verbose_name='UF')
    artigo_definido = models.CharField(max_length=10, verbose_name='Artigo Definido', blank=True, null=True)

    def __str__(self):
        return self.uf


TIPO_CHOICES = [
    ('justica_eleitoral', 'Justiça Eleitoral'),
    ('justica_estadual', 'Justiça Estadual'),
    ('justica_federal', 'Justiça Federal'),
    ('justica_trabalho', 'Justiça do Trabalho'),
]

class Justica(models.Model):
    nome = models.CharField(max_length=255)
    tipo = models.CharField(max_length=50, choices=TIPO_CHOICES)
    estado = models.ForeignKey('Estado', on_delete=models.CASCADE)
    timbrado = models.FileField(
        upload_to='timbrados_justicas/',
        validators=[validate_file_extension],
        blank=True,
        null=True,
        verbose_name='Timbrado (.docx)'
    )

    def __str__(self):
        return f"{self.nome}"

    class Meta:
        verbose_name = 'Justiças'
        verbose_name_plural = 'Justiças'



class Cidade(models.Model):
    nome = models.CharField(max_length=255, verbose_name='Nome da Cidade')
    estado = models.ForeignKey(Estado, on_delete=models.CASCADE, verbose_name='UF')
    comarca = models.BooleanField(default=False, verbose_name='É comarca')

    def __str__(self):
        return f"{self.nome} - {self.estado.uf}"


class Vara(models.Model):
    nome = models.CharField(max_length=255, verbose_name='Nome da Vara')
    comarca = models.ForeignKey('Cidade', on_delete=models.CASCADE, verbose_name='Comarca')
    justica = models.ForeignKey('Justica', on_delete=models.CASCADE, verbose_name='Justiça')
    juiz = models.CharField(max_length=255, verbose_name='Juiz', blank=True, null=True)
    juiz_substituto = models.CharField(max_length=255, verbose_name='Juiz Substituto', blank=True)
    endereco = models.CharField(max_length=255, verbose_name='Endereço', blank=True)
    numero = models.CharField(max_length=10, verbose_name='Número', blank=True)
    bairro = models.CharField(max_length=255, verbose_name='Bairro', blank=True)
    cep = BRPostalCodeField(verbose_name='CEP', blank=True)
    telefone = models.CharField(
        max_length=15,
        verbose_name='Telefone',
        blank=True,
        validators=[RegexValidator(regex=r'^\(\d{2}\) \d{4,5}-\d{4}$', message="Formato esperado: (XX) XXXXX-XXXX")]
    )
    email = models.EmailField(verbose_name='E-mail', validators=[validate_email], blank=True)
    timbrado = models.FileField(
        upload_to='timbrados_varas/',
        validators=[validate_file_extension],
        blank=True,
        null=True,
        verbose_name='Timbrado (.docx)'
    )

    def endereco_completo(self):
        partes = [
            self.endereco,
            f"nº. {self.numero}" if self.numero else "",
            self.bairro,
            f"{self.comarca.nome}/{self.comarca.estado.uf}" if self.comarca and self.comarca.estado else "",
            f"CEP {self.cep}" if self.cep else ""
        ]
        return ', '.join([parte for parte in partes if parte])

    endereco_completo.short_description = 'Endereço Completo'

    def __str__(self):
        return f"{self.nome}"


class Exequente(models.Model):
    TIPO_PESSOA_CHOICES = [
        ('PF', 'Pessoa Física'),
        ('PJ', 'Pessoa Jurídica'),
    ]

    nome = models.CharField(max_length=255)
    tipo_pessoa = models.CharField(max_length=2, choices=TIPO_PESSOA_CHOICES, verbose_name='Tipo de Pessoa')
    cpf = models.CharField(max_length=14, blank=True, null=True, verbose_name='CPF')
    cnpj = models.CharField(max_length=18, blank=True, null=True, verbose_name='CNPJ')

    def __str__(self):
        return self.nome

class Executado(models.Model):
    TIPO_PESSOA_CHOICES = [
        ('PF', 'Pessoa Física'),
        ('PJ', 'Pessoa Jurídica'),
    ]

    nome = models.CharField(max_length=255)
    tipo_pessoa = models.CharField(max_length=2, choices=TIPO_PESSOA_CHOICES, verbose_name='Tipo de Pessoa')
    cpf = models.CharField(max_length=14, blank=True, null=True, verbose_name='CPF')
    cnpj = models.CharField(max_length=18, blank=True, null=True, verbose_name='CNPJ')

    def __str__(self):
        return self.nome

class TerceiroInteressado(models.Model):
    TIPO_PESSOA_CHOICES = [
        ('PF', 'Pessoa Física'),
        ('PJ', 'Pessoa Jurídica'),
    ]

    nome = models.CharField(max_length=255)
    tipo_pessoa = models.CharField(max_length=2, choices=TIPO_PESSOA_CHOICES, verbose_name='Tipo de Pessoa')
    cpf = models.CharField(max_length=14, blank=True, null=True, verbose_name='CPF')
    cnpj = models.CharField(max_length=18, blank=True, null=True, verbose_name='CNPJ')

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = 'Terceiros Interessados'
        verbose_name_plural = 'Terceiros Interessados'


class Matricula(models.Model):
    matricula = models.CharField(max_length=50, unique=False, verbose_name='Número da Matrícula')
    estado = models.ForeignKey('Estado', on_delete=models.CASCADE, verbose_name='Estado da Matrícula')
    cidade = models.ForeignKey('Cidade', on_delete=models.CASCADE, blank=True, verbose_name='Cidade')
    rua = models.CharField(max_length=255, blank=True, verbose_name='Rua')
    numero = models.CharField(max_length=10, blank=True, verbose_name='Número')
    complemento = models.CharField(max_length=100, blank=True, verbose_name='Complemento')
    bairro = models.CharField(max_length=100, blank=True, verbose_name='Bairro')
    cep = models.CharField(max_length=9, blank=True, verbose_name='CEP')

    def __str__(self):
        return f"{self.matricula} - {self.estado.uf}"


class Leiloeiro(models.Model):
    SEXO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Feminino'),
    ]

    nome = models.CharField(max_length=255)
    cpf = models.CharField(max_length=14, unique=True, verbose_name='CPF')
    email = models.EmailField(unique=True, verbose_name='E-mail')
    telefone = models.CharField(max_length=20, blank=True)
    matriculas = models.ManyToManyField('Matricula', verbose_name='Matrículas')
    site = models.CharField(max_length=255, blank=True)
    timbrado = models.FileField(
        upload_to='timbrados/',
        null=True,
        blank=True,
        validators=[validate_file_extension],
        verbose_name='Timbrado'
    )
    sexo = models.CharField(max_length=1, choices=SEXO_CHOICES, verbose_name='Sexo')

    def __str__(self):
        return self.nome



class Leilao(models.Model):
    TIPO_CHOICES = [
        ('judicial', 'Leilão Judicial'),
        ('extrajudicial', 'Leilão Extrajudicial'),
        ('particular', 'Alienação Particular'),
        ('venda_direta', 'Venda Direta'),
    ]

    MODALIDADE_CHOICES = [
        ('eletronico', 'Eletrônica'),
        ('presencial', 'Presencial'),
        ('misto', 'Presencial e Eletrônico'),
    ]

    nome = models.CharField(max_length=255)
    tipo = models.CharField(max_length=50, choices=TIPO_CHOICES)
    modalidade = models.CharField(max_length=50, choices=MODALIDADE_CHOICES)
    local_realizacao = models.TextField(blank=True, null=True)
    processos = models.ManyToManyField(
        'Processo',
        related_name='leiloes',
        blank=True,
        verbose_name='Processos'
    )

    def __str__(self):
        datas = ', '.join(data.data_hora.strftime("%d/%m/%Y %H:%M") for data in self.datas_leilao.all())

        return f"[{self.id}] {self.nome} - Datas: {datas if datas else 'Sem datas'}"

    class Meta:
        verbose_name = 'Leilões'
        verbose_name_plural = 'Leilões'

class DataLeilao(models.Model):
    COMPLEMENTO_CHOICES = [
        ('às', 'às'),
        ('a partir das', 'a partir das')
    ]

    ETAPA_CHOICES = [
        ('unico', 'Leilão único'),
        ('primeiro', 'Primeiro Leilão'),
        ('segundo', 'Segundo Leilão'),
        ('terceiro', 'Terceiro Leilão'),
        ('quarto', 'Quarto Leilão'),
        ('quinto', 'Quinto Leilão'),
        ('sexto', 'Sexto Leilão'),
    ]

    TIPO_CHOICES = [
        ('encerramento', 'Encerramento'),
        ('inicio', 'Início'),
    ]

    leilao = models.ForeignKey(Leilao, related_name='datas_leilao', on_delete=models.CASCADE)
    etapa = models.CharField(max_length=10, choices=ETAPA_CHOICES, verbose_name='Etapa do Leilão')
    tipo_data = models.CharField(max_length=12, choices=TIPO_CHOICES, verbose_name='Tipo de Data', default='inicio')
    data_hora = models.DateTimeField(verbose_name='Data e Hora do Leilão')
    complemento = models.CharField(max_length=12, choices=COMPLEMENTO_CHOICES, default='às')
    data_abertura = models.DateTimeField(verbose_name='Data de Abertura', blank=True, null=True)

    def __str__(self):
        return f"{self.etapa} - {self.tipo_data} ({self.complemento} {self.data_hora.strftime('%d/%m/%Y %H:%M')})"

    class Meta:
        verbose_name = 'Data Leilões'
        verbose_name_plural = 'Data Leilões'


@deconstructible
class PathAndRename(object):
    def __init__(self, sub_path):
        self.path = sub_path

    def __call__(self, instance, filename):
        ext = filename.split('.')[-1]
        filename = f'{instance.processo.id}_{uuid.uuid4().hex}.{ext}'
        return os.path.join(self.path, filename)


from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Status(models.Model):
    nome = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.nome

class TipoAnexo(models.Model):
    nome = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nome


User = get_user_model()

class Processo(models.Model):
    CONFECCAO_CHOICES = [
        ('Serrano', 'Serrano'),
        ('Vara', 'Vara'),
    ]

    leiloeiro = models.ForeignKey(Leiloeiro, on_delete=models.CASCADE, null=False, blank=True, verbose_name='Leiloeiro')
    leilao = models.ForeignKey(
        Leilao,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='processos_associados',
        verbose_name='Leilão Vinculado'
    )
    confeccao = models.CharField(max_length=7, choices=CONFECCAO_CHOICES, verbose_name='Confecção')
    numero = models.CharField(max_length=25, unique=True, verbose_name='Número')
    classe_processual = models.ForeignKey(ClasseProcessual, on_delete=models.SET_NULL, null=True, blank=True,
                                          verbose_name='Classe Processual')
    vara = models.ForeignKey(Vara, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Vara')
    exequentes = models.ManyToManyField(Exequente, blank=True, verbose_name='Exequentes')
    executados = models.ManyToManyField(Executado, blank=True, verbose_name='Executados')
    terceiros_interessados = models.ManyToManyField(TerceiroInteressado, blank=True,
                                                    verbose_name='Terceiros Interessados')
    valor_divida = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,
                                       verbose_name='Valor da Dívida')
    fls_divida = models.PositiveIntegerField(
        verbose_name="Fls. da Dívida",
        validators=[MaxValueValidator(9999)],
        blank=True,
        null=True,
        help_text="Número da página do <b>PDF</b> onde o valor da dívida foi encontrado"
    )
    data_divida = models.DateField(null=True, blank=True, verbose_name='Data da Dívida')
    comissao = models.DecimalField(
        max_digits=5, decimal_places=2,
        validators=[
            MinValueValidator(0.00),
            MaxValueValidator(100.00)
        ],
        blank=True,
        null=True,
        verbose_name='Comissão (%)',
        default=5.00
    )
    onus = models.TextField(blank=True, verbose_name='Ônus')
    venda_direta = models.BooleanField(default=False, verbose_name="Venda Direta")
    observacoes = models.TextField(blank=True, null=True, verbose_name='Observações')
    list = models.ForeignKey('List', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='List')
    responsavel = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='processos_responsaveis', verbose_name='Responsável')
    preco_vil = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[
            MinValueValidator(0.00),
            MaxValueValidator(100.00)
        ],
        blank=True,
        null=True,
        verbose_name='Preço Vil (%)',
        default=0.00
    )
    data_cadastro = models.DateField(default=timezone.now, verbose_name='Data de Cadastro')

    def get_kanban_list_name(self):
        card = Card.objects.filter(processo=self).first()
        if card and card.list:
            return card.list.name
        return 'Sem coluna'

    get_kanban_list_name.short_description = 'Coluna no Kanban'

    def __str__(self):
        vara_display = self.vara.nome if self.vara else "Sem Vara"
        return f"Processo {self.numero} - {vara_display}"


from django.db import models

class Bem(models.Model):
    TIPO_BEM_CHOICES = [
        ('Automoveis', 'Automóveis'),
        ('Equipamentos', 'Equipamentos'),
        ('Imoveis', 'Imóveis'),
        ('Semoventes', 'Semoventes'),
    ]

    processo = models.ForeignKey(Processo, on_delete=models.CASCADE, related_name='bens')
    tipo_bem = models.CharField(max_length=20, choices=TIPO_BEM_CHOICES, verbose_name='Tipo do Bem')
    descricao = models.TextField(verbose_name='Descrição do Bem')
    valor = models.DecimalField(max_digits=14, decimal_places=2, verbose_name='Avaliação', null=True, blank=True)
    data_avaliacao = models.DateField(null=True, blank=True, verbose_name='Data da Avaliação')
    valor_atualizado = models.DecimalField(max_digits=14, decimal_places=2, verbose_name='Avaliação atualizada', null=True, blank=True)
    data_avaliacao_atualizada = models.DateField(null=True, blank=True, verbose_name='Data da Avaliação atualizada')
    depositario = models.TextField(blank=True, verbose_name='Depositário')
    localizacao = models.TextField(verbose_name='Localização do Bem', blank=True)

    def __str__(self):
        data_avaliacao_str = self.data_avaliacao.strftime('%d/%m/%Y') if self.data_avaliacao else "Data não disponível"
        return f"{self.get_tipo_bem_display()} - {self.descricao} - Avaliado em R$ {self.valor} em {data_avaliacao_str}"

    class Meta:
        verbose_name_plural = "Bens"


TIMBRADO_CHOICES = [
    ('none', 'Nenhum'),
    ('vara', 'Vara'),
    ('leiloeiro', 'Leiloeiro'),
]

class TipoDocumento(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    descricao = models.TextField(blank=True)

    def __str__(self):
        return self.nome


class ProcessoArquivo(models.Model):
    processo = models.ForeignKey('Processo', related_name='arquivos', on_delete=models.CASCADE, verbose_name='Processo')
    tipo_anexo = models.ForeignKey('TipoAnexo', related_name='arquivos', on_delete=models.CASCADE,
                                   verbose_name='Tipo de Anexo')
    arquivo = models.FileField(upload_to='processos_arquivos/', verbose_name='Arquivo')
    nome_arquivo = models.CharField(max_length=255, verbose_name='Nome do Arquivo')

    def __str__(self):
        return f"{self.nome_arquivo} - {self.processo.numero}"

    def clean(self):
        # Tipos de anexo que devem ser únicos
        tipos_unicos = ['EDITAL APROVADO']

        if self.tipo_anexo.nome in tipos_unicos:
            if ProcessoArquivo.objects.filter(processo=self.processo, tipo_anexo=self.tipo_anexo).exclude(
                    pk=self.pk).exists():
                raise ValidationError(f"Já existe um anexo do tipo '{self.tipo_anexo.nome}' para este processo.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class MyModel(models.Model):
    nome_modelo = models.CharField(max_length=255)
    tipo_documento = models.ForeignKey(TipoDocumento, on_delete=models.CASCADE, null=True)
    content = HTMLField('Conteúdo')
    vara = models.ForeignKey('Vara', on_delete=models.SET_NULL, null=True, blank=True, related_name='modelos_vara')
    leiloeiro = models.ForeignKey('Leiloeiro', on_delete=models.SET_NULL, null=True, blank=True, related_name='modelos_leiloeiro')
    justica = models.ForeignKey('Justica', on_delete=models.SET_NULL, null=True, blank=True,
                                related_name='modelos_justica')
    timbrado = models.CharField(max_length=10, choices=[('none', 'Nenhum'), ('vara', 'Vara'), ('leiloeiro', 'Leiloeiro'), ('justica', 'Justiça')], default='none')

    def __str__(self):
        return f"{self.nome_modelo} ({self.tipo_documento.nome if self.tipo_documento else 'Sem Tipo Documento'})"


class GrupoResponsavel(models.Model):
    nome = models.CharField(max_length=100)
    estados = models.ManyToManyField('Estado', related_name='grupos_responsaveis')
    cor_tag = models.CharField(max_length=7, default='#FFFFFF')

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = 'Grupos responsáveis'
        verbose_name_plural = 'Grupos responsáveis'


class Card(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    list = models.ForeignKey('List', related_name='cards', on_delete=models.CASCADE)
    processo = models.ForeignKey('Processo', on_delete=models.CASCADE, null=True, blank=True)
    leilao = models.ForeignKey('Leilao', on_delete=models.SET_NULL, null=True, blank=True, related_name='cards_leilao')
    vara = models.ForeignKey('Vara', on_delete=models.SET_NULL, null=True, blank=True, related_name='cards_vara')
    leiloeiro = models.ForeignKey('Leiloeiro', on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name='cards_leiloeiro')
    responsavel = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='cards_responsaveis', verbose_name='Responsável')
    grupos_responsaveis = models.ManyToManyField('GrupoResponsavel', blank=True, related_name='cards_responsaveis')
    is_aggregated = models.BooleanField(default=False)
    alto_valor = models.BooleanField(default=False, verbose_name='Alto Valor')
    data_publicacao = models.DateField(null=True, blank=True, verbose_name='Data da Publicação')
    identificador_publicjud = models.CharField(max_length=255, blank=True, null=True,
                                               verbose_name='Identificador PUBLICJUD')
    publicado = models.BooleanField(default=False, verbose_name="Publicado")

    def get_grupos_tags(self):
        tags = []
        for grupo in self.grupos_responsaveis.all():
            tag = f'<span style="background-color:{grupo.cor_tag}; color: white;">{grupo.nome}</span>'
            tags.append(tag)
        return ' '.join(tags)

    def update_groups(self):
        if self.processo and self.processo.vara and self.processo.vara.comarca:
            estado_vara = self.processo.vara.comarca.estado
            grupos = GrupoResponsavel.objects.filter(estados=estado_vara)
            self.grupos_responsaveis.set(grupos)

    def save(self, *args, **kwargs):
        update_groups = kwargs.pop('update_groups', True)
        super().save(*args, **kwargs)
        if update_groups:
            self.update_groups()

    def __str__(self):
        return self.title


class ChecklistItem(models.Model):
    card = models.ForeignKey(Card, related_name='checklist_items', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name



class Board(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class List(models.Model):
    name = models.CharField(max_length=100)
    board = models.ForeignKey(Board, related_name='lists', on_delete=models.CASCADE)
    ordem = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name


class Comment(models.Model):
    card = models.ForeignKey('Card', related_name='comments', on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    mentions = models.ManyToManyField(User, related_name='mentions', blank=True)  # Novo campo

    def __str__(self):
        return f'{self.author.username}: {self.content[:20]}'

class EmailLog(models.Model):
    subject = models.CharField(max_length=255)
    message = models.TextField()
    recipient = models.EmailField()
    status = models.CharField(max_length=10,
                              choices=[('pending', 'Pendente'), ('sent', 'Enviado'), ('failed', 'Falhou')],
                              default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.subject} to {self.recipient} ({self.status})"

class EmailTemplate(models.Model):
    name = models.CharField(max_length=100, unique=True)
    subject = models.CharField(max_length=255)
    content = models.TextField()
    trigger_list = models.ForeignKey('List', on_delete=models.CASCADE, related_name='email_templates')
    recipients = models.ManyToManyField('NotificationRecipient', blank=True, related_name='email_templates')

    def __str__(self):
        return self.name

class NotificationRecipient(models.Model):
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.email

class FrasePadrao(models.Model):
    chave = models.CharField(max_length=255, db_index=True)
    descricao = models.TextField()

    def __str__(self):
        return self.chave

    class Meta:
        verbose_name = 'Frases Padrões'
        verbose_name_plural = 'Frases Padrões'


class CardsAgregados(models.Model):
    card = models.ForeignKey('Card', on_delete=models.CASCADE, related_name='cards_agregados')
    processo = models.ForeignKey('Processo', on_delete=models.CASCADE)
    data_agregacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Card {self.card.id} agregado com Processo {self.processo.numero}"


class PenhoraExterna(models.Model):
    processo_principal = models.ForeignKey(
        'Processo',
        related_name='penhoras_externas',
        on_delete=models.CASCADE
    )
    numero = models.CharField(
        max_length=25,
        validators=[
            RegexValidator(
                regex=r'^\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}$',
                message='Número do processo deve estar no formato NNNNNNN-NN.NNNN.N.NN.NNNN',
            )
        ],
        verbose_name='Número do Processo'
    )
    vara = models.ForeignKey(
        'Vara',
        on_delete=models.CASCADE,
        verbose_name='Vara'
    )
    exequente = models.ForeignKey(
        'Exequente',
        on_delete=models.CASCADE,
        verbose_name='Exequente'
    )

    class Meta:
        verbose_name = 'Penhoras a oficiar / Pessoas a intimar'
        verbose_name_plural = 'Penhoras a oficiar / Pessoas a intimar'

    def __str__(self):
        return f'Penhora Externa {self.numero} vinculada ao Processo {self.processo_principal.numero}'