# Generated by Django 5.0.7 on 2024-11-13 06:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='ticket',
            name='ref_code',
            field=models.IntegerField(default=88888888, editable=False),
            preserve_default=False,
        ),
    ]
