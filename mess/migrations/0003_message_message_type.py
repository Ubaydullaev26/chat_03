# Generated by Django 5.1.3 on 2024-12-23 13:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mess', '0002_remove_clientsession_created_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='message_type',
            field=models.CharField(choices=[('sender', 'sender'), ('receiver', 'receiver')], default='sender', max_length=55),
            preserve_default=False,
        ),
    ]
