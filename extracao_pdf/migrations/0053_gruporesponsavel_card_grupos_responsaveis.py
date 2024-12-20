# Generated by Django 4.1 on 2024-08-04 04:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('extracao_pdf', '0052_alter_list_options_remove_list_tipos_documento'),
    ]

    operations = [
        migrations.CreateModel(
            name='GrupoResponsavel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=100)),
                ('cor_tag', models.CharField(default='#FFFFFF', max_length=7)),
                ('estado', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='grupos_responsaveis', to='extracao_pdf.estado')),
            ],
        ),
        migrations.AddField(
            model_name='card',
            name='grupos_responsaveis',
            field=models.ManyToManyField(blank=True, related_name='cards_responsaveis', to='extracao_pdf.gruporesponsavel'),
        ),
    ]
