# Generated by Django 3.0.7 on 2022-06-19 19:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wallet', '0010_remove_wallet_disabled'),
    ]

    operations = [
        migrations.AddField(
            model_name='withdraw',
            name='declined',
            field=models.BooleanField(default=False),
        ),
    ]