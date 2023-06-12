# Generated by Django 3.0.7 on 2022-07-27 09:03

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('investment', '0009_auto_20220711_2136'),
    ]

    operations = [
        migrations.AddField(
            model_name='investment',
            name='disabled',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='investment',
            name='sold',
            field=models.BooleanField(default=False),
        ),
        migrations.CreateModel(
            name='SoldInvestment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.FloatField(db_index=True, default=0.0)),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
                ('approved', models.BooleanField(default=False)),
                ('declined', models.BooleanField(default=False)),
                ('investment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='investment.Investment')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
