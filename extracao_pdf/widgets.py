from django import forms
from django.utils.numberformat import format


class CurrencyWidget(forms.TextInput):
    def __init__(self, attrs=None):
        super().__init__(attrs={'class': 'currency-input', **(attrs or {})})

    def format_value(self, value):
        if value == '' or value is None:
            return None
        return 'R$ {:.2f}'.format(float(value)).replace('.', ',')

    def value_from_datadict(self, data, files, name):
        value = data.get(name)
        if value.startswith('R$'):
            value = value[3:].strip()
        return value.replace('.', '').replace(',', '.') if value else None

class DateMaskWidget(forms.DateInput):
    class Media:
        js = ('https://cdnjs.cloudflare.com/ajax/libs/jquery/3.6.0/jquery.min.js',
              'https://cdnjs.cloudflare.com/ajax/libs/jquery.mask/1.14.16/jquery.mask.min.js',)

    def __init__(self, attrs=None):
        super().__init__(attrs={'class': 'date-mask', 'placeholder': 'dd/mm/aaaa', **(attrs or {})})

class HourMaskWidget(forms.TimeInput):
    class Media:
        js = ('https://cdnjs.cloudflare.com/ajax/libs/jquery/3.6.0/jquery.min.js',
              'https://cdnjs.cloudflare.com/ajax/libs/jquery.mask/1.14.16/jquery.mask.min.js',)

    def __init__(self, attrs=None):
        super().__init__(attrs={'class': 'hour-mask', 'placeholder': 'hh:mm', **(attrs or {})})
