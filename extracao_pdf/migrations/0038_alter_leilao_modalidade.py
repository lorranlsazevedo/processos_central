# Generated by Django 4.1 on 2024-05-17 00:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('extracao_pdf', '0037_tipodocumento_remove_mymodel_tipo_arquivo_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='leilao',
            name='modalidade',
            field=models.CharField(choices=[('eletronico', 'Eletrônica'), ('presencial', 'Presencial'), ('misto', 'Presencial e Eletrônico')], max_length=50),
        ),
    ]
