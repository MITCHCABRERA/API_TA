# Generated by Django 5.1.6 on 2025-03-17 04:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0007_post_privacy_user_role'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='privacy',
        ),
        migrations.RemoveField(
            model_name='user',
            name='role',
        ),
    ]
