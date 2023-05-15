from django.contrib import admin
from . models import doctor, Slot, Dates
from patient.models import Appointment

# Register your models here.

class DoctorAppointment(admin.TabularInline):
    model=Appointment



class doctorAdmin(admin.ModelAdmin):
    list_display=['get_name','get_id','specialization', 'address', 'mobile', 'user']
    inlines=[DoctorAppointment]

class SlotAdmin(admin.ModelAdmin):
    list_display=['id','time', 'isBooked','date']

class DateAdmin(admin.ModelAdmin):
    list_display=['id','date']

admin.site.register(doctor,doctorAdmin)
admin.site.register(Slot, SlotAdmin)
admin.site.register(Dates, DateAdmin)