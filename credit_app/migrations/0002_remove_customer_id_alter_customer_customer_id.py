# Generated by Django 5.0 on 2023-12-16 12:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('credit_app', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customer',
            name='id',
        ),
        migrations.AlterField(
            model_name='customer',
            name='customer_id',
            field=models.CharField(max_length=50, primary_key=True, serialize=False),
        ),
    ]
