# Generated by Django 4.2.17 on 2025-02-03 02:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('khanhvan', '0005_rule_rulecamera_rule_cameras'),
    ]

    operations = [
        migrations.AddField(
            model_name='rule',
            name='end_time',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='rule',
            name='start_time',
            field=models.DateTimeField(null=True),
        ),
    ]
