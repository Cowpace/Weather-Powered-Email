# Generated by Django 2.0.1 on 2018-01-15 02:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='weathermodel',
            name='city',
            field=models.TextField(primary_key=True, serialize=False),
        ),
        migrations.AlterUniqueTogether(
            name='weathermodel',
            unique_together=set(),
        ),
        migrations.RemoveField(
            model_name='weathermodel',
            name='id',
        ),
    ]
