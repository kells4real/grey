# Generated by Django 3.0.7 on 2022-06-21 21:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0007_user_referred'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='bitcoin',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]