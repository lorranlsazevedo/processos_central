# Generated by Django 4.1 on 2024-11-06 16:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('extracao_pdf', '0109_bem_data_avaliacao_atualizada_bem_valor_atualizado'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='penhoraexterna',
            options={'verbose_name': 'Penhoras a oficiar / Pessoas a intimar', 'verbose_name_plural': 'Penhoras a oficiar / Pessoas a intimar'},
        ),
        migrations.AlterField(
            model_name='bem',
            name='valor',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=14, null=True, verbose_name='Avaliação'),
        ),
    ]
