# Generated by Django 3.1.6 on 2021-03-04 17:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('regel', '0002_auto_20210223_1341'),
    ]

    operations = [
        migrations.AlterField(
            model_name='regel',
            name='name',
            field=models.CharField(max_length=100),
        ),
    ]
