# Generated by Django 3.0.7 on 2022-05-28 11:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0002_user_refereecodeliteral'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='referenceCode',
            field=models.CharField(max_length=10, unique=True),
        ),
    ]
