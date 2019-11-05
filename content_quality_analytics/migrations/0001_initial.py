# Generated by Django 2.2.4 on 2019-10-23 10:36

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uid', models.CharField(max_length=255)),
                ('src', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Module',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uid', models.CharField(max_length=255)),
                ('mod_name', models.CharField(max_length=255)),
                ('mod_type', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Scale',
            fields=[
                ('name', models.CharField(max_length=255, primary_key=True, serialize=False)),
                ('type', models.CharField(max_length=255)),
                ('attr', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Session',
            fields=[
                ('id', models.CharField(max_length=255, primary_key=True, serialize=False)),
                ('active', models.BooleanField()),
            ],
        ),
    ]
