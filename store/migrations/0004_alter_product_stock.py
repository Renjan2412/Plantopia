# Generated by Django 4.2.1 on 2023-07-10 13:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0003_alter_picture_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='stock',
            field=models.IntegerField(default=0),
        ),
    ]
