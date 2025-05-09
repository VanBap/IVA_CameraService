# Generated by Django 4.2.17 on 2025-03-17 03:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('khanhvan', '0030_alter_vlmmodel_api_key'),
    ]

    operations = [
        migrations.CreateModel(
            name='TestImage',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('created_by', models.BigIntegerField(null=True)),
                ('updated_by', models.BigIntegerField(null=True)),
                ('url', models.CharField(blank=True, default='', max_length=255)),
            ],
            options={
                'db_table': 'test_image',
                'managed': True,
            },
        ),
    ]
