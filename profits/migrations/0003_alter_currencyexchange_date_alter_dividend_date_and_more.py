# Generated by Django 5.1.2 on 2024-11-14 17:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profits', '0002_alter_account_user_broker_ref_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='currencyexchange',
            name='date',
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name='dividend',
            name='date',
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name='split',
            name='date',
            field=models.DateField(),
        ),
    ]