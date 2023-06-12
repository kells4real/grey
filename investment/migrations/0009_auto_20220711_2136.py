# Generated by Django 3.0.7 on 2022-07-11 20:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('investment', '0008_auto_20220624_0052'),
    ]

    operations = [
        migrations.AlterField(
            model_name='portfolio',
            name='profit_frequency',
            field=models.CharField(choices=[('Weekly', 'Weekly'), ('Monthly', 'Monthly'), ('90 Days', '90 Days'), ('180 Days', '180 Days'), ('365 Days', '365 Days')], default='Monthly', max_length=50),
        ),
    ]
