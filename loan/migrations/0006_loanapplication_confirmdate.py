# Generated by Django 3.0.7 on 2022-07-31 21:11

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('loan', '0005_loanapplication_confirmed_by'),
    ]

    operations = [
        migrations.AddField(
            model_name='loanapplication',
            name='confirmDate',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
