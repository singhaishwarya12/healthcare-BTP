import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from doctor.models import doctor
from user.models import User

# Create your models here.
def upload_To(instance, filename):
    return 'images/{filename}'.format(filename=filename)

class patient(models.Model):
    age= models.DecimalField(max_digits=4,decimal_places=1)
    address= models.TextField()
    mobile=models.CharField(max_length=20)
    pic = models.ImageField(upload_to=upload_To, blank=True ,null=True)
    email = models.EmailField(verbose_name = "email", max_length = 60)
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    @property
    def get_name(self):
        return self.user.first_name+" "+self.user.last_name
    @property
    def get_id(self):
        return self.user.id
    def __str__(self):
        return self.user.username 
    

class Treatment(models.Model):

    Surgery = 'S'
    Cardiology = 'C'
    Dermatalogy = 'DT'
    ENT = 'ENT'
    Gynecology = 'G'
    Neurology = 'N'
    Orthopedic = 'OP'
    Pediatric = 'PT'
    Physiotherapy = 'PY'

    treatment_choices = [
        (Surgery, 'Surgery'),
        (Cardiology,'Cardiology'),
        (Dermatalogy, 'Dermatalogy'),
        (ENT, 'ENT'),
        (Gynecology , 'Gynaecology'),
        (Neurology, 'Neurology'),
        (Orthopedic, 'Orthopedic'),
        (Pediatric, 'Pediatric'),
        (Physiotherapy, 'Physiotherapy'),
    ]
    treatment_category = models.CharField(max_length=3, choices=treatment_choices, default=ENT)
    
    def __str__(self):
        return self.treatment_category


class Appointment(models.Model):
    STATUSES = (
        ('new', 'New'),
        ('confirmed', 'confirmed'),
        ('cancelled', 'cancelled'),
        ('completed', 'completed')
    )
    status =  models.CharField(choices=STATUSES, default='new', max_length=15)
    meeting_link = models.TextField(null=True)
    doctor = models.ForeignKey(doctor, on_delete=models.CASCADE)
    patient = models.ForeignKey(patient, on_delete=models.CASCADE)
    symptoms = models.TextField()
    appointment_date=models.DateField(verbose_name="Appointment date",auto_now=False, auto_now_add=False)
    appointment_time=models.TimeField(verbose_name="Appointement time", auto_now=False, auto_now_add=False)

    def __str__(self):
        return str(self.id)+' '+self.status+' appointment for '+self.patient.get_name+' under Dr. '+self.doctor.get_name
    @property
    def get_id(self):
        return self.id

class Feedback(models.Model):
    given = models.BooleanField(default=False)
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    comment = models.TextField(blank=True)


class Prescription(models.Model):
    doctor = models.ForeignKey(doctor, on_delete=models.CASCADE)
    patient = models.ForeignKey(patient, on_delete=models.CASCADE)
    category = models.ForeignKey(Treatment, on_delete=models.CASCADE)
    diagnosis = models.TextField(max_length=400)
    medicine = models.TextField()
    tips = models.TextField()
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE)

    @property
    def get_appointment_details(self):
        return {self.appointment.appointment_date, self.appointment.appointment_time}
    
    @property
    def get_symptoms(self):
        return self.appointment.symptoms

    def __str__(self):
        return self.patient.get_name+' prescribed by Dr. '+self.doctor.get_name


class TestReport(models.Model):
    patient = models.ForeignKey(patient, on_delete=models.CASCADE)
    test_name = models.CharField(max_length=20)
    report = models.FileField(upload_to='pdfs/', null=True, blank=True)
    test_date = models.DateField()

    def __str__(self):
        return self.patient.get_name+' - '+self.test_name