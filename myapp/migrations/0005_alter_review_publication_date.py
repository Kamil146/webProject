# Generated by Django 4.1.7 on 2023-05-10 18:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0004_alter_user_username'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='publication_date',
            field=models.DateField(auto_now=True, verbose_name='published on:'),
        ),
    ]