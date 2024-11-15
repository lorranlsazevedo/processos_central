# Generated by Django 4.1 on 2024-03-13 04:12

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('extracao_pdf', '0009_processo_comissao'),
    ]

    operations = [
        migrations.AddField(
            model_name='processo',
            name='depositario',
            field=models.TextField(blank=True, verbose_name='Depositário'),
        ),
        migrations.AddField(
            model_name='processo',
            name='onus',
            field=models.TextField(blank=True, verbose_name='Ônus'),
        ),
        migrations.AlterField(
            model_name='processo',
            name='comissao',
            field=models.DecimalField(blank=True, decimal_places=2, default=5.0, max_digits=5, null=True, validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(100.0)], verbose_name='Comissão (%)'),
        ),
    ]
