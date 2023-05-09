from django.db import models
from django.db.models.fields import DateField
from user.models import User

def upload_To(instance, filename):
    return 'images/{filename}'.format(filename=filename)

# Create your models here.

class doctor(models.Model):
    Surgery = 'S'
    Cardiology = 'C'
    Dermatalogy = 'DT'
    ENT = 'ENT'
    Gynecology = 'G'
    Neurology = 'N'
    Orthopedic = 'OP'
    Pediatric = 'PT'
    Physiotherapy = 'PY'

    department_choices = [
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
    department=models.CharField(max_length=3, choices=department_choices, default=Cardiology)
    address= models.TextField()
    mobile=models.CharField(max_length=20)
    email = models.EmailField(verbose_name='email', max_length=60)
    pic = models.ImageField(upload_to=upload_To, blank=True ,null=True)
    #available_slots = models.ForeignKey(Dates, on_delete=models.CASCADE)
    user=models.OneToOneField(User,on_delete=models.CASCADE)

    @property
    def get_name(self):
        return self.user.first_name+" "+self.user.last_name
    @property
    def get_id(self):
        return self.user.id
    def __str__(self):
        return "{} ({})".format(self.user.first_name,self.department)

class Slot(models.Model):
    time = models.TimeField()
    isBooked = models.BooleanField(default=False)


class Dates(models.Model):
    date = models.DateField(verbose_name='Date')
    slots = models.ForeignKey(Slot, on_delete=models.CASCADE)
    doctor_id = models.ForeignKey(doctor, on_delete=models.CASCADE)

    """def fn():
        return Slot.objects.filter(isBooked=False)"""
