from django.contrib import admin
from . models import patient, Appointment, Feedback, Medicine, Prescription, TestReport, TreatmentHistory, AllowedAppointments

# Register your models here.

class AppointmentAdmin(admin.ModelAdmin):
    list_display=('id','status','appointment_date','appointment_time')

class PatientAdmin(admin.ModelAdmin):
    list_display=('get_name','user','age','address','mobile')


class FeedbackAdmin(admin.ModelAdmin):
    list_display=('id','rating','comment')

class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ('get_dr','get_patient','get_appointment')


class MedicineAdmin(admin.ModelAdmin):
    list_display = ('name','type')

class TestReportAdmin(admin.ModelAdmin):
    list_display = ('get_patient','test_name','get_dr')

class TreatmentHistoryAdmin(admin.ModelAdmin):
    list_display = ('id','get_patient','get_dr')

class AllowedAdmin(admin.ModelAdmin):
    list_display = ('get_app','get_patient','allowed')

admin.site.register(Medicine,MedicineAdmin)
admin.site.register(Prescription,PrescriptionAdmin)
admin.site.register(TestReport,TestReportAdmin)
admin.site.register(Appointment, AppointmentAdmin)
admin.site.register(patient, PatientAdmin)
admin.site.register(Feedback, FeedbackAdmin)
admin.site.register(TreatmentHistory,TreatmentHistoryAdmin)
admin.site.register(AllowedAppointments,AllowedAdmin)