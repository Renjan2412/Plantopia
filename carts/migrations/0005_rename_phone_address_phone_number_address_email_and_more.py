# Generated by Django 4.2.1 on 2023-07-19 12:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('carts', '0004_address'),
    ]

    operations = [
        migrations.RenameField(
            model_name='address',
            old_name='phone',
            new_name='phone_number',
        ),
        migrations.AddField(
            model_name='address',
            name='email',
            field=models.EmailField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='address',
            name='first_name',
            field=models.CharField(default='', max_length=50),
        ),
        migrations.AddField(
            model_name='address',
            name='last_name',
            field=models.CharField(default='', max_length=50),
        ),
        migrations.AddField(
            model_name='address',
            name='order_note',
            field=models.CharField(blank=True, max_length=200),
        ),
    ]