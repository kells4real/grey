# Generated by Django 3.0.7 on 2022-06-22 09:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('loan', '0004_remove_loanapplication_date_approved'),
    ]

    operations = [
        migrations.AddField(
            model_name='loanapplication',
            name='confirmed_by',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
