from django import forms
from .models import Processo, Leiloeiro, Vara, MyModel, ProcessoArquivo, EmailTemplate, Bem, PenhoraExterna, \
    Matricula, DataLeilao, Executado, Exequente, TerceiroInteressado
from tinymce.widgets import TinyMCE
from django.core.validators import EmailValidator, RegexValidator
from .widgets import CurrencyWidget, DateMaskWidget, HourMaskWidget
from django.core.exceptions import ValidationError
import re
from dal import autocomplete
from datetime import datetime
from django.utils import timezone


def validate_file_extension(value):
    if not value.name.endswith('.docx'):
        raise forms.ValidationError('Este campo aceita apenas arquivos .docx.')


def validate_cpf_or_cnpj(value):
    # Remove todos os caracteres não numéricos
    value = re.sub(r'\D', '', value)

    if len(value) == 11:
        # Validação CPF
        def calc_dv(cpf, length):
            weights = range(length + 1, 1, -1)
            dv = sum(int(digit) * weight for digit, weight in zip(cpf[:length], weights)) % 11
            return 0 if dv < 2 else 11 - dv

        if not value.isdigit() or calc_dv(value, 9) != int(value[9]) or calc_dv(value, 10) != int(value[10]):
            raise ValidationError('CPF inválido.')
    elif len(value) == 14:
        # Validação CNPJ
        def calc_dv(cnpj, length):
            weights = (5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2) if length == 12 else (6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2)
            dv = sum(int(digit) * weight for digit, weight in zip(cnpj[:length], weights)) % 11
            return 0 if dv < 2 else 11 - dv

        if not value.isdigit() or calc_dv(value, 12) != int(value[12]) or calc_dv(value, 13) != int(value[13]):
            raise ValidationError('CNPJ inválido.')
    else:
        raise ValidationError('CPF ou CNPJ inválido.')


# Formulário Leiloeiro
class LeiloeiroForm(forms.ModelForm):
    timbrado = forms.FileField(
        validators=[validate_file_extension],
        required=False,
        label='Timbrado (.docx)',
        help_text='Faça upload de um arquivo .docx'
    )
    cpf = forms.CharField(
        max_length=14,
        widget=forms.TextInput(attrs={'class': 'cpf-mask'}),
        validators=[validate_cpf_or_cnpj],
        label='CPF'
    )
    telefone = forms.CharField(
        max_length=15,
        widget=forms.TextInput(attrs={'class': 'form-control telefone-mask'}),
        required=False
    )
    email = forms.EmailField(
        required=False,
        validators=[EmailValidator()],
        widget=forms.EmailInput(attrs={'class': 'form-control email-input'})
    )

    def clean_site(self):
        site = self.cleaned_data.get('site')
        if site and site.startswith("http://"):
            site = site.replace("http://", "")
        elif site and site.startswith("https://"):
            site = site.replace("https://", "")
        return site

    class Meta:
        model = Leiloeiro
        fields = ['nome', 'cpf', 'email', 'telefone', 'matriculas', 'site', 'timbrado']


# Formulário Vara
class VaraForm(forms.ModelForm):
    telefone = forms.CharField(
        max_length=15,
        widget=forms.TextInput(attrs={'class': 'form-control telefone-mask'}),
        required=False
    )
    cep = forms.CharField(
        max_length=9,
        widget=forms.TextInput(attrs={'class': 'form-control cep-mask'}),
        required=False
    )
    email = forms.EmailField(
        required=False,
        validators=[EmailValidator()],
        widget=forms.EmailInput(attrs={'class': 'form-control email-input'})
    )

    class Meta:
        model = Vara
        fields = '__all__'


# Formulário MyModel
class MyModelForm(forms.ModelForm):
    class Meta:
        model = MyModel
        fields = '__all__'
        widgets = {
            'content': TinyMCE(attrs={'cols': 80, 'rows': 30}),
        }

    def clean(self):
        cleaned_data = super().clean()
        tipo_documento = cleaned_data.get('tipo_documento')
        if not tipo_documento:
            raise forms.ValidationError("Tipo de Documento é obrigatório.")
        return cleaned_data


# Formulário EmailTemplate
class EmailTemplateForm(forms.ModelForm):
    class Meta:
        model = EmailTemplate
        fields = '__all__'
        widgets = {
            'content': TinyMCE(attrs={'cols': 80, 'rows': 30}),
        }


# Formulário Processo
class ProcessoForm(forms.ModelForm):
    numero = forms.CharField(
        max_length=25,
        widget=forms.TextInput(attrs={'class': 'form-control processo-mask'}),
        validators=[RegexValidator(
            regex=r'^\d{7}-\d{2}\.\d{4}\.\d{1}\.\d{2}\.\d{4}$',
            message="Formato esperado: 0000455-51.2020.5.23.0081"
        )],
        required=True
    )

    valor_divida = forms.CharField(widget=CurrencyWidget(), required=False)
    data_divida = forms.DateField(widget=DateMaskWidget(), required=False)

    class Meta:
        model = Processo
        fields = '__all__'

    def clean_valor_divida(self):
        valor_divida = self.cleaned_data.get('valor_divida')
        return valor_divida if valor_divida else None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Personalizar o widget do campo 'leiloeiro'
        leiloeiro_widget = self.fields['leiloeiro'].widget
        leiloeiro_widget.can_add_related = False
        leiloeiro_widget.can_delete_related = False
        leiloeiro_widget.can_change_related = False

        # Personalizar o widget do campo 'leilao'
        leilao_widget = self.fields['leilao'].widget
        leilao_widget.can_add_related = True
        leilao_widget.can_change_related = True


class BemForm(forms.ModelForm):
    valor = forms.DecimalField(widget=CurrencyWidget(), required=False)
    valor_atualizado = forms.DecimalField(widget=CurrencyWidget(), required=False)
    data_avaliacao = forms.DateField(widget=DateMaskWidget(), required=False)
    data_avaliacao_atualizada = forms.DateField(widget=DateMaskWidget(), required=False)

    class Meta:
        model = Bem
        fields = '__all__'


# Formulário Penhora Externa
class PenhoraExternaForm(forms.ModelForm):
    numero = forms.CharField(
        max_length=25,
        widget=forms.TextInput(attrs={'class': 'form-control processo-mask'}),
        validators=[RegexValidator(
            regex=r'^\d{7}-\d{2}\.\d{4}\.\d{1}\.\d{2}\.\d{4}$',
            message="Formato esperado: 0000455-51.2020.5.23.0081"
        )],
        required=True
    )

    class Meta:
        model = PenhoraExterna
        fields = ['numero', 'vara', 'exequente']

    class Media:
        js = ('path/to/your/mask.js',)
        css = {
            'all': ('path/to/your/styles.css',)
        }


# Formulário Matricula
class MatriculaForm(forms.ModelForm):
    class Meta:
        model = Matricula
        fields = '__all__'

    def clean_matricula(self):
        matricula = self.cleaned_data.get('matricula')
        if Matricula.objects.filter(matricula=matricula).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("O número da matrícula deve ser único. Já existe uma matrícula com este número.")
        return matricula


# Formulário Data Leilão
class DataLeilaoForm(forms.ModelForm):
    data = forms.DateField(widget=DateMaskWidget(), required=True, label="Data do Leilão")
    hora = forms.TimeField(widget=HourMaskWidget(), required=True, label="Hora do Leilão")

    data_abertura_data = forms.DateField(widget=DateMaskWidget(), required=False, label="Data de Abertura")
    data_abertura_hora = forms.TimeField(widget=HourMaskWidget(), required=False, label="Hora de Abertura")

    class Meta:
        model = DataLeilao
        fields = ('leilao', 'etapa', 'tipo_data', 'complemento')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            if self.instance.data_hora:
                data_hora_local = timezone.localtime(self.instance.data_hora)
                self.fields['data'].initial = data_hora_local.date()
                self.fields['hora'].initial = data_hora_local.time()

            if self.instance.data_abertura:
                data_abertura_local = timezone.localtime(self.instance.data_abertura)
                self.fields['data_abertura_data'].initial = data_abertura_local.date()
                self.fields['data_abertura_hora'].initial = data_abertura_local.time()

    def clean(self):
        cleaned_data = super().clean()
        data = cleaned_data.get('data')
        hora = cleaned_data.get('hora')

        if data and hora:
            cleaned_data['data_hora'] = datetime.combine(data, hora)

        data_abertura_data = cleaned_data.get('data_abertura_data')
        data_abertura_hora = cleaned_data.get('data_abertura_hora')

        if data_abertura_data and data_abertura_hora:
            cleaned_data['data_abertura'] = datetime.combine(data_abertura_data, data_abertura_hora)

        return cleaned_data

    def save(self, commit=True):
        self.instance.data_hora = self.cleaned_data.get('data_hora')
        self.instance.data_abertura = self.cleaned_data.get('data_abertura')
        return super().save(commit=commit)


validate_cpf = RegexValidator(
    regex=r'^\d{3}\.\d{3}\.\d{3}-\d{2}$',
    message="Formato esperado: 000.000.000-00"
)

# Validador de CNPJ (para 14 dígitos)
validate_cnpj = RegexValidator(
    regex=r'^\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}$',
    message="Formato esperado: 00.000.000/0000-00"
)

class ExequenteForm(forms.ModelForm):
    cpf = forms.CharField(
        max_length=14,
        widget=forms.TextInput(attrs={'class': 'cpf-mask'}),
        validators=[validate_cpf],
        label='CPF',
        required=False
    )
    cnpj = forms.CharField(
        max_length=18,
        widget=forms.TextInput(attrs={'class': 'cnpj-mask'}),
        validators=[validate_cnpj],
        label='CNPJ',
        required=False
    )

    class Meta:
        model = Exequente
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        cpf = cleaned_data.get('cpf')
        cnpj = cleaned_data.get('cnpj')

        if not cpf and not cnpj:
            raise forms.ValidationError("Por favor, preencha o CPF ou o CNPJ.")

        if cpf and cnpj:
            raise forms.ValidationError("Por favor, preencha apenas o CPF ou o CNPJ, não ambos.")

        return cleaned_data


class ExecutadoForm(forms.ModelForm):
    cpf = forms.CharField(
        max_length=14,
        widget=forms.TextInput(attrs={'class': 'cpf-mask'}),
        validators=[validate_cpf],
        label='CPF',
        required=False
    )
    cnpj = forms.CharField(
        max_length=18,
        widget=forms.TextInput(attrs={'class': 'cnpj-mask'}),
        validators=[validate_cnpj],
        label='CNPJ',
        required=False
    )

    class Meta:
        model = Executado
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        cpf = cleaned_data.get('cpf')
        cnpj = cleaned_data.get('cnpj')

        if not cpf and not cnpj:
            raise forms.ValidationError("Por favor, preencha o CPF ou o CNPJ.")

        if cpf and cnpj:
            raise forms.ValidationError("Por favor, preencha apenas o CPF ou o CNPJ, não ambos.")

        return cleaned_data

class TerceiroInteressadoForm(forms.ModelForm):
    cpf = forms.CharField(
        max_length=14,
        widget=forms.TextInput(attrs={'class': 'cpf-mask'}),
        validators=[validate_cpf],
        label='CPF',
        required=False
    )
    cnpj = forms.CharField(
        max_length=18,
        widget=forms.TextInput(attrs={'class': 'cnpj-mask'}),
        validators=[validate_cnpj],
        label='CNPJ',
        required=False
    )

    class Meta:
        model = TerceiroInteressado
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        cpf = cleaned_data.get('cpf')
        cnpj = cleaned_data.get('cnpj')

        if not cpf and not cnpj:
            raise forms.ValidationError("Por favor, preencha o CPF ou o CNPJ.")

        if cpf and cnpj:
            raise forms.ValidationError("Por favor, preencha apenas o CPF ou o CNPJ, não ambos.")

        return cleaned_data

class UploadArquivoForm(forms.ModelForm):
    class Meta:
        model = ProcessoArquivo
        fields = ['processo', 'tipo_anexo', 'arquivo', 'nome_arquivo']
