# Generated by Django 2.2.6 on 2021-12-13 11:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0007_auto_20211203_1647'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='image',
            field=models.ImageField(blank=True, help_text='Картинка для поста', upload_to='posts/', verbose_name='картинка'),
        ),
    ]
