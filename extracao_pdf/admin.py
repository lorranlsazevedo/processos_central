from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from .models import (Processo, Board, List, Card, Status, ClasseProcessual, Justica, Estado, Vara,
                     NotificationRecipient,
                     Cidade, TipoDocumento, ProcessoArquivo, Exequente, Executado, TerceiroInteressado, FrasePadrao,
                     Bem, Leiloeiro, Matricula, Leilao, DataLeilao, GrupoResponsavel, TipoAnexo, EmailLog,
                     EmailTemplate, PenhoraExterna)
from .models import MyModel
from tinymce.widgets import TinyMCE
from django.db import models
from django.utils.formats import number_format
from django.utils.timezone import localtime
from .forms import LeiloeiroForm, VaraForm, MyModelForm, UploadArquivoForm, EmailTemplateForm, ProcessoForm, BemForm, \
    PenhoraExternaForm, MatriculaForm, DataLeilaoForm, ExequenteForm, ExecutadoForm, TerceiroInteressadoForm
from extracao_pdf.views import GruposResponsaveisFilter, LeilaoAutocomplete
import openpyxl
from django.http import HttpResponse
from django.utils.translation import gettext_lazy as _
from django.urls import path
from dal import autocomplete


@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

@admin.register(List)
class ListAdmin(admin.ModelAdmin):
    list_display = ['name', 'board', 'ordem']
    search_fields = ['name']
    list_filter = ['board']

@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ['title', 'list', 'processo', 'responsavel']
    search_fields = ['title']
    list_filter = ['list', GruposResponsaveisFilter]
    list_per_page = 25

@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    list_display = ['nome']
    search_fields = ['nome']


@admin.register(ClasseProcessual)
class ClasseProcessualAdmin(admin.ModelAdmin):
    search_fields = ['nome']

    def has_delete_permission(self, request, obj=None):
        # Não permite exclusão de varas
        return False


@admin.register(Estado)
class EstadoAdmin(admin.ModelAdmin):
    list_display = ['uf', 'nome']
    search_fields = ['uf', 'nome']


@admin.register(Justica)
class JusticaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'tipo', 'estado', 'timbrado_display')
    list_filter = ['tipo', 'estado']
    search_fields = ['nome']
    list_per_page = 25

    def timbrado_display(self, obj):
        if obj.timbrado:
            return format_html("<a href='{}'>Download</a>", obj.timbrado.url)
        return "Nenhum arquivo"
    timbrado_display.short_description = 'Timbrado'


@admin.register(Cidade)
class CidadeAdmin(admin.ModelAdmin):
    list_display = ['nome', 'estado', 'comarca']
    list_filter = ['estado', 'comarca']
    search_fields = ['nome', 'estado__nome', 'estado__uf']
    list_select_related = ['estado']
    list_per_page = 50


@admin.register(Vara)
class VaraAdmin(admin.ModelAdmin):
    form = VaraForm
    list_display = ['nome', 'comarca', 'justica', 'telefone', 'email', 'ver_timbrado']
    list_filter = ['justica']
    search_fields = ['nome', 'juiz', 'juiz_substituto', 'comarca__nome', 'justica__nome', 'bairro', 'cep', 'telefone', 'email']
    list_per_page = 25

    def ver_timbrado(self, obj):
        if obj.timbrado:
            return format_html("<a href='{}'>Download</a>", obj.timbrado.url)
        return "Nenhum arquivo"
    ver_timbrado.short_description = 'Timbrado'

    def has_delete_permission(self, request, obj=None):
        # Não permite exclusão de varas
        return False

@admin.register(Exequente)
class ExequenteAdmin(admin.ModelAdmin):
    form = ExequenteForm
    list_display = ['nome', 'tipo_pessoa']
    search_fields = ('nome', 'cpf', 'cnpj')
    list_per_page = 25


@admin.register(Executado)
class ExecutadoAdmin(admin.ModelAdmin):
    form = ExecutadoForm
    list_display = ['nome', 'tipo_pessoa']
    search_fields = ('nome', 'cpf', 'cnpj')
    list_per_page = 25


@admin.register(TerceiroInteressado)
class TerceiroInteressadoAdmin(admin.ModelAdmin):
    form = TerceiroInteressadoForm
    list_display = ['nome', 'tipo_pessoa']
    search_fields = ('nome', 'cpf', 'cnpj')
    list_per_page = 25


class BemInline(admin.StackedInline):
    model = Bem
    form = BemForm
    extra = 1


@admin.register(Matricula)
class MatriculaAdmin(admin.ModelAdmin):
    form = MatriculaForm
    list_display = ['matricula', 'estado']
    search_fields = ['estado__nome']
    autocomplete_fields = ['estado', 'cidade']
    list_per_page = 25


@admin.register(Leiloeiro)
class LeiloeiroAdmin(admin.ModelAdmin):
    form = LeiloeiroForm
    list_display = ['nome', 'email', 'site', 'ver_timbrado']
    search_fields = ['nome', 'cpf', 'email', 'sexo']
    autocomplete_fields = ['matriculas']
    list_per_page = 25

    def ver_timbrado(self, obj):
        if obj.timbrado:
            return format_html("<a href='{url}'>Download</a>", url=obj.timbrado.url)
        else:
            return "Nenhum arquivo"

    ver_timbrado.short_description = 'Timbrado'


class ProcessoArquivoInline(admin.StackedInline):
    model = ProcessoArquivo
    form = UploadArquivoForm
    extra = 1


@admin.action(description='Exportar Processos para XLSX')
def exportar_processos_xlsx(modeladmin, request, queryset):
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="processos.xlsx"'

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Processos"

    # Cabeçalhos
    ws.append(['Número', 'Leiloeiro', 'Leilão', 'Vara', 'Coluna no Kanban'])

    for processo in queryset:
        ws.append([
            processo.numero,
            processo.leiloeiro.nome if processo.leiloeiro else 'N/A',
            processo.leilao.nome if processo.leilao else 'N/A',
            processo.vara.nome if processo.vara else 'N/A',
            processo.get_kanban_list_name(),
        ])

    wb.save(response)
    return response

class PenhoraExternaInline(admin.StackedInline):
    model = PenhoraExterna
    form = PenhoraExternaForm
    extra = 1

@admin.register(Processo)
class ProcessoAdmin(admin.ModelAdmin):
    form = ProcessoForm
    actions = [exportar_processos_xlsx]
    list_display = ['numero', 'leiloeiro', 'vara', 'leilao', 'get_primeira_data_leilao', 'get_kanban_list_name', 'escolher_documento_link']
    list_filter = ('confeccao', 'leiloeiro', 'responsavel')
    autocomplete_fields = ['classe_processual', 'exequentes', 'executados', 'terceiros_interessados', 'vara']
    search_fields = ['numero', 'vara__nome', 'leilao__nome', 'bens__descricao']
    inlines = [BemInline, PenhoraExternaInline, ProcessoArquivoInline]
    list_per_page = 25

    fieldsets = (
        (None, {
            'fields': (
            'responsavel', 'leiloeiro', 'leilao', 'confeccao', 'numero', 'classe_processual', 'vara', 'exequentes',
            'executados', 'terceiros_interessados', 'valor_divida', 'fls_divida', 'data_divida', 'comissao', 'preco_vil',
            'onus', 'venda_direta')
        }),
        ('Observações', {
            'fields': ('observacoes',),
            'classes': ('collapse',),
        }),
    )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)

        if db_field.name == 'leiloeiro':
            formfield.widget.can_add_related = False
            formfield.widget.can_delete_related = False

        if db_field.name == 'leilao':
            formfield.widget.can_add_related = True
            formfield.widget.can_delete_related = True

        return formfield

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('leilao-autocomplete/', LeilaoAutocomplete.as_view(), name='leilao-autocomplete'),
        ]
        return custom_urls + urls

    def escolher_documento_link(self, obj):
        url = reverse('escolher_documento', args=[obj.pk])
        return format_html('<a href="{}">Escolher Documento</a>', url)
    escolher_documento_link.short_description = 'Escolher Documento'

    def get_primeira_data_leilao(self, obj):
        leiloes = obj.leiloes.all()
        if leiloes:
            primeiro_leilao = leiloes.first()
            datas = primeiro_leilao.datas_leilao.all().order_by('data_hora')
            if datas:
                primeira_data = localtime(datas.first().data_hora)  # Ajuste para local timezone
                return primeira_data.strftime("%d/%m/%Y %H:%M")
        return "Sem data"
    get_primeira_data_leilao.short_description = 'Primeira Data do Leilão'

    def valor_divida_reais(self, obj):
        if obj.valor_divida is not None:
            return "R$ {}".format(number_format(obj.valor_divida, 2))
        return "N/A"
    valor_divida_reais.short_description = 'Valor da Dívida'

    def add_view(self, request, form_url='', extra_context=None):
        numero_processo_temp = request.GET.get('numero_processo')

        if numero_processo_temp:
            if not extra_context:
                extra_context = {}
            extra_context['numero_processo'] = numero_processo_temp

        return super(ProcessoAdmin, self).add_view(request, form_url, extra_context)

    def get_form(self, request, obj=None, **kwargs):
        """
        Personaliza o formulário para ocultar ou mostrar as opções de adicionar/excluir
        """
        form = super().get_form(request, obj, **kwargs)

        form.base_fields['leiloeiro'].required = True
        form.base_fields['vara'].required = True

        form.base_fields['leiloeiro'].widget.can_add_related = False
        form.base_fields['leiloeiro'].widget.can_delete_related = False
        form.base_fields['leiloeiro'].widget.can_change_related = False

        form.base_fields['leilao'].widget.can_add_related = True
        #form.base_fields['leilao'].widget.can_delete_related = True
        form.base_fields['leilao'].widget.can_change_related = True


        return form


def get_changeform_initial_data(self, request):
    initial = super().get_changeform_initial_data(request)
    numero_processo = request.session.pop('numero_processo_temp', None)
    if numero_processo:
        initial['numero'] = numero_processo
    return initial


@admin.register(MyModel)
class MyModelAdmin(admin.ModelAdmin):
    list_display = ('nome_modelo', 'get_tipo_documento_display', 'get_leiloeiro_display', 'get_vara_display', 'get_justica_display', 'timbrado_display')
    list_filter = ['leiloeiro', 'tipo_documento', 'timbrado']
    search_fields = ['nome_modelo', 'content']
    list_per_page = 25

    def get_tipo_documento_display(self, obj):
        return obj.tipo_documento.nome if obj.tipo_documento else 'Não definido'
    get_tipo_documento_display.short_description = 'Tipo de Documento'

    def get_leiloeiro_display(self, obj):
        return obj.leiloeiro.nome if obj.leiloeiro else '-'
    get_leiloeiro_display.short_description = 'Leiloeiro'

    def get_vara_display(self, obj):
        return obj.vara.nome if obj.vara else '-'
    get_vara_display.short_description = 'Vara'

    def get_justica_display(self, obj):
        return obj.justica.nome if obj.justica else '-'
    get_justica_display.short_description = 'Justiça'

    def timbrado_display(self, obj):
        if obj.timbrado == 'vara' and obj.vara and obj.vara.timbrado:
            return format_html("<a href='{}'>Download</a>", obj.vara.timbrado.url)
        elif obj.timbrado == 'leiloeiro' and obj.leiloeiro and obj.leiloeiro.timbrado:
            return format_html("<a href='{}'>Download</a>", obj.leiloeiro.timbrado.url)
        elif obj.timbrado == 'justica' and obj.justica and obj.justica.timbrado:
            return format_html("<a href='{}'>Download</a>", obj.justica.timbrado.url)
        return "Nenhum arquivo"
    timbrado_display.short_description = 'Timbrado'

    form = MyModelForm

    formfield_overrides = {
        models.TextField: {'widget': TinyMCE()},
    }

class DataLeilaoInline(admin.StackedInline):
    form = DataLeilaoForm
    model = DataLeilao
    form = DataLeilaoForm
    extra = 1


@admin.register(DataLeilao)
class DataLeilaoAdmin(admin.ModelAdmin):
    form = DataLeilaoForm
    list_display = ('leilao', 'etapa', 'tipo_data', 'data_hora', 'data_abertura')
    list_per_page = 25
    fields = ('leilao', 'etapa', 'tipo_data', 'complemento', 'data', 'hora', 'data_abertura_data', 'data_abertura_hora')


@admin.register(Leilao)
class LeilaoAdmin(admin.ModelAdmin):
    list_display = ['id', 'nome', 'tipo', 'modalidade', 'get_primeira_data', 'get_ultima_data']
    search_fields = ['nome']
    filter_horizontal = ('processos',)
    inlines = [DataLeilaoInline]
    ordering = ['nome']
    list_per_page = 25

    def get_search_results(self, request, queryset, search_term):
        if search_term.isdigit():
            queryset = queryset.filter(id=search_term)
            use_distinct = False
        else:
            queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        return queryset, use_distinct

    def get_primeira_data(self, obj):
        datas = obj.datas_leilao.all().order_by('data_hora')
        if datas:
            primeira_data = datas.first()
            return primeira_data.data_hora.strftime("%d/%m/%Y %H:%M")
        return "Sem data"

    get_primeira_data.short_description = 'Primeira Data'

    def get_ultima_data(self, obj):
        datas = obj.datas_leilao.all().order_by('data_hora')
        if datas:
            ultima_data = datas.last()
            return ultima_data.data_hora.strftime("%d/%m/%Y %H:%M")
        return "Sem data"

    get_ultima_data.short_description = 'Última Data'


@admin.register(TipoDocumento)
class TipoDocumentoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'descricao']
    search_fields = ['nome', 'descricao']

@admin.register(GrupoResponsavel)
class GrupoResponsavelAdmin(admin.ModelAdmin):
    list_display = ['nome', 'display_estados', 'cor_tag']
    search_fields = ['nome']
    filter_horizontal = ('estados',)

    def display_estados(self, obj):
        return ", ".join([estado.uf for estado in obj.estados.all()])
    display_estados.short_description = 'Estados'

    fieldsets = (
        (None, {
            'fields': ('nome', 'estados', 'cor_tag')
        }),
    )

@admin.register(TipoAnexo)
class TipoAnexoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome')
    search_fields = ('nome',)
    ordering = ('nome',)

class ProcessoArquivoAdmin(admin.ModelAdmin):
    list_display = ['processo', 'tipo_anexo', 'arquivo', 'nome_arquivo']
    fields = ['processo', 'arquivo', 'nome_arquivo', 'tipo_anexo']

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['tipo_anexo']
        return []

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        if obj and obj.tipo_anexo.nome == "EDITAL APROVADO":
            return False
        return super().has_change_permission(request, obj)

admin.site.register(ProcessoArquivo, ProcessoArquivoAdmin)


@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    list_display = ('subject', 'recipient', 'status', 'created_at', 'sent_at')
    list_filter = ('status', 'created_at')
    search_fields = ('subject', 'recipient')
    list_per_page = 25

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_view_permission(self, request, obj=None):
        return True

@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    form = EmailTemplateForm
    list_display = ('name', 'subject', 'trigger_list_display')
    list_filter = ['trigger_list']
    search_fields = ['name', 'subject', 'content']
    list_per_page = 25

    def trigger_list_display(self, obj):
        return obj.trigger_list.name
    trigger_list_display.short_description = 'Trigger List'


@admin.register(NotificationRecipient)
class NotificationRecipientAdmin(admin.ModelAdmin):
    list_display = ('email',)
    search_fields = ('email',)


@admin.register(FrasePadrao)
class FrasePadraoAdmin(admin.ModelAdmin):
    list_display = ('chave', 'descricao')
    search_fields = ('chave', 'descricao')
    list_filter = ('chave',)
    list_per_page = 25