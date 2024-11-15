# Generated by Django 4.1 on 2024-10-31 18:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('extracao_pdf', '0104_remove_executado_cpf_remove_exequente_cpf_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='executado',
            name='documento',
        ),
        migrations.RemoveField(
            model_name='exequente',
            name='documento',
        ),
        migrations.RemoveField(
            model_name='terceirointeressado',
            name='documento',
        ),
        migrations.AddField(
            model_name='executado',
            name='cnpj',
            field=models.CharField(blank=True, max_length=18, null=True, verbose_name='CNPJ'),
        ),
        migrations.AddField(
            model_name='executado',
            name='cpf',
            field=models.CharField(blank=True, max_length=14, null=True, verbose_name='CPF'),
        ),
        migrations.AddField(
            model_name='exequente',
            name='cnpj',
            field=models.CharField(blank=True, max_length=18, null=True, verbose_name='CNPJ'),
        ),
        migrations.AddField(
            model_name='exequente',
            name='cpf',
            field=models.CharField(blank=True, max_length=14, null=True, verbose_name='CPF'),
        ),
        migrations.AddField(
            model_name='terceirointeressado',
            name='cnpj',
            field=models.CharField(blank=True, max_length=18, null=True, verbose_name='CNPJ'),
        ),
        migrations.AddField(
            model_name='terceirointeressado',
            name='cpf',
            field=models.CharField(blank=True, max_length=14, null=True, verbose_name='CPF'),
        ),
    ]
