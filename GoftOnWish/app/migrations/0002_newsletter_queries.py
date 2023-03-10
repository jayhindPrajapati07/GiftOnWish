# Generated by Django 4.1.4 on 2022-12-29 11:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Newsletter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=60)),
                ('consent', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Queries',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=60)),
                ('email', models.EmailField(max_length=60)),
                ('subject', models.CharField(max_length=60)),
                ('message', models.TextField()),
                ('is_resolved', models.BooleanField(default=False)),
            ],
        ),
    ]
