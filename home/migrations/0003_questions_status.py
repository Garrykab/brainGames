# Generated by Django 5.0.7 on 2024-07-16 04:18

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0002_questions"),
    ]

    operations = [
        migrations.AddField(
            model_name="questions",
            name="status",
            field=models.IntegerField(default=0),
        ),
    ]
