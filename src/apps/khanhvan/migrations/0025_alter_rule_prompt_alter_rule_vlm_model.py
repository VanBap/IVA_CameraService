# Generated by Django 4.2.17 on 2025-03-10 07:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('khanhvan', '0024_rename_apikey_vlmmodel_api_key'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rule',
            name='prompt',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='rules', to='khanhvan.prompt'),
        ),
        migrations.AlterField(
            model_name='rule',
            name='vlm_model',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='rules', to='khanhvan.vlmmodel'),
        ),
    ]
