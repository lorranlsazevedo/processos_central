# Generated by Django 4.1 on 2024-04-09 04:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('extracao_pdf', '0024_remove_leiloeiro_site_alter_leiloeiro_cpf_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='leiloeiro',
            name='site',
            field=models.URLField(default='www'),
            preserve_default=False,
        ),
    ]
