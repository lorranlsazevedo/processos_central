# Generated by Django 4.1 on 2024-08-08 20:26

from django.db import migrations, models
import extracao_pdf.models


class Migration(migrations.Migration):

    dependencies = [
        ('extracao_pdf', '0055_list_tipos_documento'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='list',
            name='tipos_documento',
        ),
        migrations.AlterField(
            model_name='processoarquivo',
            name='arquivo',
            field=models.FileField(upload_to=extracao_pdf.models.PathAndRename('processos_arquivos/'), verbose_name='Arquivo'),
        ),
    ]
