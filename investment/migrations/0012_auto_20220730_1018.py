# Generated by Django 3.0.7 on 2022-07-30 09:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('investment', '0011_soldinvestment_approvedby'),
    ]

    operations = [
        migrations.RenameField(
            model_name='soldinvestment',
            old_name='approvedBy',
            new_name='confirmedBy',
        ),
    ]
