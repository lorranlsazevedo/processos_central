# Generated by Django 4.1 on 2024-08-21 18:53

import django.core.validators
from django.db import migrations, models
import localflavor.br.models


class Migration(migrations.Migration):

    dependencies = [
        ('extracao_pdf', '0068_delete_logentry'),
    ]

    operations = [
        migrations.AddField(
            model_name='vara',
            name='bairro',
            field=models.CharField(blank=True, max_length=255, verbose_name='Bairro'),
        ),
        migrations.AddField(
            model_name='vara',
            name='cep',
            field=localflavor.br.models.BRPostalCodeField(blank=True, max_length=9, verbose_name='CEP'),
        ),
        migrations.AddField(
            model_name='vara',
            name='email',
            field=models.EmailField(blank=True, max_length=254, validators=[django.core.validators.EmailValidator()], verbose_name='E-mail'),
        ),
        migrations.AddField(
            model_name='vara',
            name='endereco',
            field=models.CharField(blank=True, max_length=255, verbose_name='Endereço'),
        ),
        migrations.AddField(
            model_name='vara',
            name='numero',
            field=models.CharField(blank=True, max_length=10, verbose_name='Número'),
        ),
        migrations.AddField(
            model_name='vara',
            name='telefone',
            field=models.CharField(blank=True, max_length=15, validators=[django.core.validators.RegexValidator(message='Formato esperado: (XX) XXXXX-XXXX', regex='^\\(\\d{2}\\) \\d{4,5}-\\d{4}$')], verbose_name='Telefone'),
        ),
    ]
