# Generated by Django 3.2.18 on 2023-04-25 08:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0002_alter_productinfo_external_id'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='user',
            options={'ordering': ('email',), 'verbose_name': 'User', 'verbose_name_plural': 'Users list'},
        ),
    ]
