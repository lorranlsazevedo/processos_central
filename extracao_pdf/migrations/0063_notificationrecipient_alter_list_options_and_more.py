# Generated by Django 4.1 on 2024-08-12 02:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('extracao_pdf', '0062_emaillog_delete_emailtemplate_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='NotificationRecipient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254, unique=True)),
            ],
        ),
        migrations.AlterModelOptions(
            name='list',
            options={},
        ),
        migrations.CreateModel(
            name='EmailTemplate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('subject', models.CharField(max_length=255)),
                ('content', models.TextField()),
                ('recipients', models.ManyToManyField(blank=True, related_name='email_templates', to='extracao_pdf.notificationrecipient')),
                ('trigger_list', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='email_templates', to='extracao_pdf.list')),
            ],
        ),
    ]
