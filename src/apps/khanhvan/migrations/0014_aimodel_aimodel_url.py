# Generated by Django 4.2.17 on 2025-03-05 08:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('khanhvan', '0013_aimodel_ruleprompt_rulecamera_unique_rule_camera'),
    ]

    operations = [
        migrations.AddField(
            model_name='aimodel',
            name='aimodel_url',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
    ]
