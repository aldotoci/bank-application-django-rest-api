# Generated by Django 5.1.2 on 2024-10-14 16:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('banking', '0016_remove_transaction_card_remove_transaction_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='transaction_id',
            field=models.CharField(max_length=30, unique=True),
        ),
    ]
