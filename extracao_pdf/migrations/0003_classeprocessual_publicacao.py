# Generated by Django 4.1 on 2024-03-10 13:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('extracao_pdf', '0002_classeprocessual_processo_classe_processual'),
    ]

    operations = [
        migrations.AddField(
            model_name='classeprocessual',
            name='publicacao',
            field=models.CharField(choices=[('Interno', 'Interno'), ('Externo', 'Externo')], default='Interno', max_length=7),
        ),
    ]
