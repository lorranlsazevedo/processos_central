# Generated by Django 4.1 on 2024-08-04 04:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('extracao_pdf', '0053_gruporesponsavel_card_grupos_responsaveis'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='gruporesponsavel',
            name='estado',
        ),
        migrations.AddField(
            model_name='gruporesponsavel',
            name='estados',
            field=models.ManyToManyField(related_name='grupos_responsaveis', to='extracao_pdf.estado'),
        ),
    ]
