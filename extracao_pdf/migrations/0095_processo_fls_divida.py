# Generated by Django 4.1 on 2024-10-10 23:20

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('extracao_pdf', '0094_alter_matricula_matricula'),
    ]

    operations = [
        migrations.AddField(
            model_name='processo',
            name='fls_divida',
            field=models.PositiveIntegerField(blank=True, help_text='Número da folha onde o valor da dívida foi encontrado (máximo de 4 dígitos)', null=True, validators=[django.core.validators.MaxValueValidator(9999)], verbose_name='Folha da Dívida'),
        ),
    ]
