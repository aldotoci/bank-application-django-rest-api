# Generated by Django 5.1.2 on 2024-10-14 10:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('banking', '0014_bankaccount_balance_alter_bankaccount_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='card',
            name='date',
            field=models.DateField(auto_now=True),
        ),
    ]
