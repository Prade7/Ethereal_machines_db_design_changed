# Generated by Django 5.1 on 2024-08-28 23:42

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Machine',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=50)),
                ('acceleration', models.FloatField()),
                ('velocity', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('employee_id', models.CharField(max_length=50, unique=True)),
                ('password_hash', models.CharField(max_length=128)),
                ('role', models.CharField(max_length=50)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='DynamicData',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('actual_position', models.JSONField(default=dict)),
                ('distance_to_go', models.JSONField(default=dict)),
                ('homed', models.JSONField(default=dict)),
                ('tool_offset', models.JSONField(default=dict)),
                ('created_by', models.CharField(max_length=50)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('machine_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='dynamic_data', to='machines_app.machine')),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='machines_app.user')),
            ],
        ),
    ]
