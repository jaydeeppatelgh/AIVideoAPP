# Generated by Django 4.2.8 on 2024-01-04 07:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0008_remove_uploadfiles_uploaded_file_path_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='uploadfiles',
            name='uploaded_file',
            field=models.FileField(blank=True, null=True, upload_to='uploaded_files/'),
        ),
    ]
