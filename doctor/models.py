from django.db import models
from django.db.models.fields import DateField
from user.models import User

def upload_To(instance, filename):
    return 'images/{filename}'.format(filename=filename)

# Create your models here.

class doctor(models.Model):

    department_choices = (
        ('Rheumatologist','Rheumatologist'),
        ('ENT_specialist', 'ENT_specialist'),
        ('Cardiologist','Cardiologist'),
        ('Orthopedist', 'Orthopedist'),
        ('Neurologist', 'Neurologist'),
        ('Allergist_Immunologist' , 'Allergist_Immunologist'),
        ('Urologist', 'Urologist'),
        ('Dermatologist','Dermatologist'),
        ('Gastroenterologist', 'Gastroenterologist'),
        ('Ophthalmologist', 'Ophthalmologist'),
        ('General Physician', 'General Physician'),
        ('obstetrics and gynaecologist','obstetrics and gynaecologist'),
        ('paediatrician','paediatrician'),
        ('psychiatrist','psychiatrist'),
        ('Surgeon','Surgeon')
    )
    specialization=models.CharField(max_length=50, choices=department_choices, default='General Physician')
    feesperSession = models.CharField(max_length=10)
    address= models.TextField()
    mobile=models.CharField(max_length=20)
    email = models.EmailField(verbose_name='email', max_length=60)
    pic = models.ImageField(upload_to=upload_To, blank=True ,null=True)
    pincode = models.CharField(max_length=10)
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    gender=models.CharField(max_length=10)
    clinic_name=models.CharField(max_length=100)
    registration_num = models.IntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['mobile', 'email','user'], name='dr_unique')
        ]

    class Meta:
        ordering = ['specialization']

    @property
    def get_name(self):
        return f"{self.user.first_name} {self.user.last_name}"
        #return self.user.first_name+" "+self.user.last_name
    @property
    def get_id(self):
        return self.id
    def __str__(self):
        return "{} ({})".format(self.user.first_name,self.specialization)

class Dates(models.Model):
    date = models.DateField(verbose_name='Date')
    #slots = models.ForeignKey(Slot, on_delete=models.CASCADE, related_name='dates')
    doctor_id = models.ForeignKey(doctor, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['doctor_id', 'date'], name='date_dr_unique')
        ]

class Slot(models.Model):
    time = models.TimeField()
    isBooked = models.BooleanField(default=False)
    date = models.ForeignKey(Dates,on_delete=models.CASCADE,related_name='slot')

    @property
    def get_date(self):
        return self.date.date
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['time', 'date'], name='date_time_unique')
        ]

