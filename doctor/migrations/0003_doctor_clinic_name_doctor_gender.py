# Generated by Django 4.2 on 2023-05-15 12:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('doctor', '0002_alter_doctor_specialization'),
    ]

    operations = [
        migrations.AddField(
            model_name='doctor',
            name='clinic_name',
            field=models.CharField(default='cl', max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='doctor',
            name='gender',
            field=models.CharField(default='male', max_length=10),
            preserve_default=False,
        ),
    ]
