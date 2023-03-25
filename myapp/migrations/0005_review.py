# Generated by Django 4.1.7 on 2023-03-25 21:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0004_alter_book_category_alter_category_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.IntegerField(choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5'), (6, '6')])),
                ('comment', models.TextField()),
                ('publication_date', models.DateField(verbose_name='published on:')),
                ('book', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='myapp.book')),
            ],
        ),
    ]
