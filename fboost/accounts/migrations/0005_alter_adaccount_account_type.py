# Generated by Django 5.1.3 on 2024-12-13 18:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_profile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='adaccount',
            name='account_type',
            field=models.CharField(choices=[('Credit Line', 'Credit Line'), ('Card', 'Card'), ('Other', 'Other')], default='Card', max_length=20),
        ),
    ]
