# Generated by Django 4.1 on 2024-08-02 00:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('extracao_pdf', '0050_remove_list_tipo_documento_list_modelos'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='list',
            name='modelos',
        ),
        migrations.AddField(
            model_name='list',
            name='tipos_documento',
            field=models.ManyToManyField(blank=True, related_name='lists', to='extracao_pdf.tipodocumento'),
        ),
    ]
