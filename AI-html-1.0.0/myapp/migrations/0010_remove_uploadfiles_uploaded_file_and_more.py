# Generated by Django 4.2.8 on 2024-01-04 11:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0009_uploadfiles_uploaded_file'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='uploadfiles',
            name='uploaded_file',
        ),
        migrations.AddField(
            model_name='uploadfiles',
            name='upload_video_1',
            field=models.FileField(blank=True, null=True, upload_to='videos/'),
        ),
        migrations.AddField(
            model_name='uploadfiles',
            name='upload_video_2',
            field=models.FileField(blank=True, null=True, upload_to='videos/'),
        ),
        migrations.AddField(
            model_name='uploadfiles',
            name='upload_video_3',
            field=models.FileField(blank=True, null=True, upload_to='videos/'),
        ),
        migrations.AddField(
            model_name='uploadfiles',
            name='upload_video_4',
            field=models.FileField(blank=True, null=True, upload_to='videos/'),
        ),
        migrations.AddField(
            model_name='uploadfiles',
            name='upload_video_5',
            field=models.FileField(blank=True, null=True, upload_to='videos/'),
        ),
        migrations.AddField(
            model_name='uploadfiles',
            name='upload_video_6',
            field=models.FileField(blank=True, null=True, upload_to='videos/'),
        ),
        migrations.AddField(
            model_name='uploadfiles',
            name='upload_video_7',
            field=models.FileField(blank=True, null=True, upload_to='videos/'),
        ),
        migrations.AddField(
            model_name='uploadfiles',
            name='upload_video_8',
            field=models.FileField(blank=True, null=True, upload_to='videos/'),
        ),
        migrations.AddField(
            model_name='uploadfiles',
            name='upload_video_9',
            field=models.FileField(blank=True, null=True, upload_to='videos/'),
        ),
    ]
