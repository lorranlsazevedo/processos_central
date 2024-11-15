# Generated by Django 4.1 on 2024-03-11 00:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('extracao_pdf', '0004_estado_justica'),
    ]

    operations = [
        migrations.AlterField(
            model_name='estado',
            name='nome',
            field=models.CharField(max_length=100, verbose_name='Nome'),
        ),
        migrations.AlterField(
            model_name='estado',
            name='uf',
            field=models.CharField(max_length=2, unique=True, verbose_name='UF'),
        ),
        migrations.CreateModel(
            name='Cidade',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=255, verbose_name='Nome da Cidade')),
                ('comarca', models.BooleanField(default=False, verbose_name='[E comarca?')),
                ('estado', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='extracao_pdf.estado', verbose_name='UF')),
            ],
        ),
    ]
