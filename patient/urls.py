from .views import (registrationView, 
                    CustomAuthToken,
                    patientProfileView,
                    patientHistoryView,
                    appointmentViewPatient2,
                    FeedbackView,
                    SlotView2,
                    upcomingAppointmentView,
                    previousAppointmentView,
                    PrescriptionView,
                    TestReportView,
                    GetDrView,
                    DrFeedbackView,
                    DoctorSearchView,
                    patientPendingRequestView)
from .PdfDowloadView import pdf
from .AlarmView import AlarmView
from django.urls import path


urlpatterns = [
    path('signup/', registrationView.as_view(), name='api_patient_registration'),
    path('login/', CustomAuthToken.as_view(), name='api_patient_login'),
    path('profile/', patientProfileView.as_view(), name='api_patient_profile'),

    path('get-dr/',GetDrView.as_view(),name='api_list_dr'),
    path('get-dr/<int:pk>/',GetDrView.as_view(),name='api_list_dr'),

    path('get-slots/', SlotView2.as_view(), name='api_patient_slots_view'),
    #to list all appointments -not to be used by frontend
    path('appointment/', appointmentViewPatient2.as_view(), name='api_patient_appointment'),

    path('appointment/<int:pk>/', appointmentViewPatient2.as_view(), name='api_patient_appointment_detail'),
    path('appointment/<int:pk>/feedback/', FeedbackView.as_view(), name='api_patient_feedback'),

    path('appointment/pending-requests/',patientPendingRequestView.as_view()),

    path('upcoming-appointment/', upcomingAppointmentView.as_view(), name='api_patient_upcoming-appointment'),
    path('upcoming-appointment/<int:pk>/', upcomingAppointmentView.as_view(), name='api_patient_upcoming-appointment_detail'),

    
    path('previous-appointment/', previousAppointmentView.as_view(), name='api_patient_previous-appointment'),
    path('previous-appointment/<int:pk>/', previousAppointmentView.as_view(), name='api_patient_previous-appointment_detail'),

    path('test-report/', TestReportView.as_view(), name='api_patient_test_Report'),
    path('test-report/<int:pk>/', TestReportView.as_view(), name='api_patient_test_Report_detail'),

    path('prescription/', PrescriptionView.as_view(), name='api_patient_prescription'),

    #useless - history is useless
    path('history/', patientHistoryView.as_view(), name='api_patient_history'),

    path('doctor/<int:pk>/feedback/',DrFeedbackView.as_view(),name='api_dr_feedback'),

    path('doctor-search/', DoctorSearchView.as_view(), name='doctor-search'),

    path('pdf/<int:pk>/', pdf.as_view(), name='pdf'), #pk - appointment id
    path('alarm/', AlarmView.as_view()),
]