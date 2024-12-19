# Generated by Django 5.1.3 on 2024-12-19 08:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_loginhistory'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='location',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='profile',
            name='timezone',
            field=models.CharField(default='UTC', max_length=50),
        ),
    ]