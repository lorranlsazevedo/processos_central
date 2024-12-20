# Generated by Django 4.1 on 2024-04-24 03:03

from django.db import migrations, models
import extracao_pdf.validators


class Migration(migrations.Migration):

    dependencies = [
        ('extracao_pdf', '0031_alter_leilao_modalidade_alter_leilao_tipo'),
    ]

    operations = [
        migrations.AddField(
            model_name='leiloeiro',
            name='timbrado',
            field=models.FileField(blank=True, null=True, upload_to='timbrados/', validators=[extracao_pdf.validators.validate_file_extension], verbose_name='Timbrado'),
        ),
    ]
