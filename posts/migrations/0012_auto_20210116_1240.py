# Generated by Django 2.2.6 on 2021-01-16 12:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0011_post_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='./media/'),
        ),
    ]