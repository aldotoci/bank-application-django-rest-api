# Generated by Django 5.1.2 on 2024-10-14 14:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('banking', '0015_alter_card_date'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='transaction',
            name='card',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='user',
        ),
    ]
