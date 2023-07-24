# Generated by Django 4.2.1 on 2023-07-14 05:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_userprofile'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='default_addr',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='phone',
            field=models.CharField(default=None, max_length=20),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='post_code',
            field=models.CharField(default=None, max_length=15),
        ),
    ]
