# Generated by Django 4.1 on 2024-03-13 03:53

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('extracao_pdf', '0008_processo_data_divida_processo_valor_divida'),
    ]

    operations = [
        migrations.AddField(
            model_name='processo',
            name='comissao',
            field=models.DecimalField(blank=True, decimal_places=2, default=5.0, help_text='Informe a porcentagem da comissão.', max_digits=5, null=True, validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(100.0)], verbose_name='Comissão (%)'),
        ),
    ]
