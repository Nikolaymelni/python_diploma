# Generated by Django 3.2.18 on 2023-04-24 15:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productinfo',
            name='external_id',
            field=models.PositiveIntegerField(verbose_name='External ID'),
        ),
    ]
