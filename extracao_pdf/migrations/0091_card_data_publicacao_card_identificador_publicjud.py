# Generated by Django 4.1 on 2024-10-05 14:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('extracao_pdf', '0090_alter_bem_valor'),
    ]

    operations = [
        migrations.AddField(
            model_name='card',
            name='data_publicacao',
            field=models.DateField(blank=True, null=True, verbose_name='Data da Publicação'),
        ),
        migrations.AddField(
            model_name='card',
            name='identificador_publicjud',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Identificador PUBLICJUD'),
        ),
    ]
