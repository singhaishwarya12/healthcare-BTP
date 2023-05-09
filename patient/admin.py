from django.contrib import admin
from . models import patient, Appointment, Feedback

# Register your models here.

class AppointmentAdmin(admin.ModelAdmin):
    list_display=('id','status','appointment_date','appointment_time')
admin.site.register(Appointment, AppointmentAdmin)

class PatientAdmin(admin.ModelAdmin):
    list_display=('user','age','address','mobile')

admin.site.register(patient, PatientAdmin)
class FeedbackAdmin(admin.ModelAdmin):
    list_display=('id','rating','comment')
admin.site.register(Feedback, FeedbackAdmin)