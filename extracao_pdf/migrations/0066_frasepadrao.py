# Generated by Django 4.1 on 2024-08-20 03:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('extracao_pdf', '0065_remove_emailtemplate_anexos_checklistitem'),
    ]

    operations = [
        migrations.CreateModel(
            name='FrasePadrao',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('chave', models.CharField(db_index=True, max_length=255)),
                ('descricao', models.TextField()),
            ],
        ),
    ]