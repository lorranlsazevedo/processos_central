# Generated by Django 4.1 on 2024-10-31 18:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('extracao_pdf', '0103_alter_dataleilao_options_executado_cpf_exequente_cpf_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='executado',
            name='cpf',
        ),
        migrations.RemoveField(
            model_name='exequente',
            name='cpf',
        ),
        migrations.RemoveField(
            model_name='terceirointeressado',
            name='cpf',
        ),
        migrations.AddField(
            model_name='executado',
            name='documento',
            field=models.CharField(blank=True, max_length=18, null=True, verbose_name='CPF/CNPJ'),
        ),
        migrations.AddField(
            model_name='exequente',
            name='documento',
            field=models.CharField(blank=True, max_length=18, null=True, verbose_name='CPF/CNPJ'),
        ),
        migrations.AddField(
            model_name='terceirointeressado',
            name='documento',
            field=models.CharField(blank=True, max_length=18, null=True, verbose_name='CPF/CNPJ'),
        ),
    ]
