# Generated by Django 4.2.8 on 2024-01-04 06:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0007_uploadfiles_uploaded_file_path_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='uploadfiles',
            name='uploaded_file_path',
        ),
        migrations.RemoveField(
            model_name='workspace',
            name='uploaded_file_path',
        ),
    ]
