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
    pincode = models.CharField(max_length=10)
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    gender = models.CharField(max_length=10)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['mobile', 'email','user'], name='patient_unique')
        ]

    @property
    def get_name(self):
        return self.user.first_name+" "+self.user.last_name
    @property
    def get_id(self):
        return self.id
    def __str__(self):
        return self.user.username 
 
class TreatmentHistory(models.Model):
    patient = models.ForeignKey(patient,on_delete=models.CASCADE, related_name='history')
    doctor = models.ForeignKey(doctor,on_delete=models.CASCADE)   

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['patient', 'doctor'], name='patient_dr_unique')
        ]

    def get_dr(self):
        return self.doctor.user.first_name +' '+ self.doctor.user.last_name
    get_dr.short_description = 'Doctor'
    
    def get_patient(self):
        return self.patient.user.first_name +' '+ self.patient.user.last_name
    get_patient.short_description = 'Patient'

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
    treatment_history = models.ForeignKey(TreatmentHistory,on_delete=models.CASCADE, related_name='appointment')
    appointment_date=models.DateField(verbose_name="Appointment date",auto_now=False, auto_now_add=False)
    appointment_time=models.TimeField(verbose_name="Appointement time", auto_now=False, auto_now_add=False)

    class Meta:
        ordering = ['appointment_date']

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
    dr = models.ForeignKey(doctor, on_delete=models.CASCADE, related_name='feedback')

class Prescription(models.Model):
    Doctor = models.ForeignKey(doctor, on_delete=models.CASCADE)
    Patient = models.ForeignKey(patient, on_delete=models.CASCADE)
    diagnosis = models.TextField(max_length=400)
    advice = models.TextField()
    test_required = models.TextField()
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name='prescription')

    @property
    def get_appointment_details(self):
        return {self.appointment.appointment_date, self.appointment.appointment_time}
    
    @property
    def get_symptoms(self):
        return self.appointment.symptoms
    
    def get_dr(self):
        return self.Doctor.user.first_name +' '+ self.Doctor.user.last_name
    get_dr.short_description = 'Doctor'
    
    def get_patient(self):
        return self.Patient.user.first_name +' '+ self.Patient.user.last_name
    get_patient.short_description = 'Patient'

    def get_appointment(self):
        return self.appointment.id
    get_appointment.short_description = 'Appointment ID'

    def __str__(self):
        return self.Patient.get_name+' prescribed by '+self.Doctor.get_name

class Medicine(models.Model):
    med_types = (
        ('Liquid','Liquid'),
        ('Tablet','Tablet'),
        ('Capsule','Capsule'),
        ('Drop','Drop'),
        ('Ointment','Ointment'),
        ('Injection','Injection')
    )
    name = models.CharField(max_length=200)
    type = models.CharField(choices=med_types,default='Tablet',max_length=10)
    duration = models.TextField()
    times = models.TextField()
    dosage = models.TextField()
    With = models.TextField()
    prescription = models.ForeignKey(Prescription,on_delete=models.CASCADE, related_name='medicine')

class TestReport(models.Model):
    patient = models.ForeignKey(patient, on_delete=models.CASCADE, related_name='report')
    test_name = models.CharField(max_length=20)
    report = models.FileField(upload_to='pdfs/', null=True, blank=True)
    test_date = models.DateField()
    dr = models.CharField(max_length=100)

    class Meta:
        ordering = ['test_date']

    def get_patient(self):
        return self.patient.user.first_name
    get_patient.short_description = 'Patient'

    def get_dr(self):
        return self.dr
    get_dr.short_description = 'Refered By (Doctor)'

    def __str__(self):
        return self.patient.user.first_name+' - '+self.test_name
    
class AllowedAppointments(models.Model):
    patient = models.ForeignKey(patient,on_delete=models.CASCADE,related_name='allowed_app')
    # the below appointment is the one which is allowing the doctor to view restricted history
    allowing_appointment = models.ForeignKey(Appointment,on_delete=models.CASCADE,related_name='allowed_appointments')
    allowed = models.IntegerField()

    def get_patient(self):
        return self.patient.user.first_name
    get_patient.short_description = 'Patient'

    def get_app(self):
        return self.allowing_appointment.get_id
    get_app.short_description = 'Allowing app id'
