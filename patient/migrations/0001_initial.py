# Generated by Django 4.2 on 2023-05-03 10:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('doctor', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Appointment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('new', 'New'), ('in_progress', 'In Progress'), ('cancelled', 'Cancelled'), ('completed', 'Completed'), ('queried', 'Queried')], default='new', max_length=15)),
                ('symptoms', models.TextField()),
                ('appointment_date', models.DateField(verbose_name='Appointment date')),
                ('appointment_time', models.TimeField(verbose_name='Appointement time')),
            ],
        ),
        migrations.CreateModel(
            name='patient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('age', models.DecimalField(decimal_places=1, max_digits=4)),
                ('address', models.TextField()),
                ('mobile', models.CharField(max_length=20)),
                ('pic', models.ImageField(null=True, upload_to='profile-pic/')),
                ('email', models.EmailField(max_length=60, verbose_name='email')),
            ],
        ),
        migrations.CreateModel(
            name='Treatment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('treatment_category', models.CharField(choices=[('S', 'Surgery'), ('C', 'Cardiology'), ('DT', 'Dermatalogy'), ('ENT', 'ENT'), ('G', 'Gynaecology'), ('N', 'Neurology'), ('OP', 'Orthopedic'), ('PT', 'Pediatric'), ('PY', 'Physiotherapy')], default='ENT', max_length=3)),
            ],
        ),
        migrations.CreateModel(
            name='TestReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('test_name', models.CharField(max_length=20)),
                ('report', models.FileField(blank=True, null=True, upload_to='pdfs/')),
                ('test_date', models.DateField()),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='patient.patient')),
            ],
        ),
        migrations.CreateModel(
            name='Prescription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('diagnosis', models.TextField(max_length=400)),
                ('medicine', models.TextField()),
                ('tips', models.TextField()),
                ('appointment', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='patient.appointment')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='patient.treatment')),
                ('doctor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='doctor.doctor')),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='patient.patient')),
            ],
        ),
    ]