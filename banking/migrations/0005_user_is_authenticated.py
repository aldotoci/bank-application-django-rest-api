# Generated by Django 5.1.2 on 2024-10-12 12:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('banking', '0004_remove_user_token'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_authenticated',
            field=models.BooleanField(default=False),
        ),
    ]
