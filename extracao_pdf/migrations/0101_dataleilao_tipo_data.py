# Generated by Django 4.1 on 2024-10-20 16:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('extracao_pdf', '0100_remove_dataleilao_tem_abertura_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='dataleilao',
            name='tipo_data',
            field=models.CharField(choices=[('encerramento', 'Encerramento'), ('inicio', 'Início')], default='inicio', max_length=12, verbose_name='Tipo de Data'),
        ),
    ]