# Generated by Django 4.2.17 on 2025-01-16 03:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('khanhvan', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CameraAlert',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('name', models.CharField(max_length=255)),
                ('camera_id', models.IntegerField(default=0)),
                ('type', models.CharField(default='', max_length=255)),
                ('desc', models.CharField(default='', max_length=255)),
            ],
            options={
                'db_table': 'camera_alert',
                'managed': False,
            },
        ),
    ]
