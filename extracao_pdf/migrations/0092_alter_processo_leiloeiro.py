# Generated by Django 4.1 on 2024-10-06 23:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('extracao_pdf', '0091_card_data_publicacao_card_identificador_publicjud'),
    ]

    operations = [
        migrations.AlterField(
            model_name='processo',
            name='leiloeiro',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='extracao_pdf.leiloeiro', verbose_name='Leiloeiro'),
        ),
    ]
