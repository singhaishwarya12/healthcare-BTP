"""
/
    /registration
    /login
    /profile
    /upcmoing-appointments
    /upcmoing-appointments/:id
    /previous-appointments
    /previous-appointments/:id
/treatment-history
/treatment-history/:id
/treatments-ongoing
/treatments-ongoing/:id
    /test-reports
    /test-reports/:id
/:uuid
/logout
"""

from .views import (registrationView, 
                    CustomAuthToken,
                    patientProfileView,
                    patientHistoryView,
                    appointmentViewPatient,
                    FeedbackView,
                    upcomingAppointmentView,
                    previousAppointmentView,
                    TestReportView)
from django.urls import path


urlpatterns = [
    path('signup/', registrationView.as_view(), name='api_patient_registration'),
    path('login/', CustomAuthToken.as_view(), name='api_patient_login'),
    path('profile/', patientProfileView.as_view(), name='api_patient_profile'),
    #path('book-appointment/', bookAppointmentView.as_view(), name='api_patient_book_Appointment'),
    path('appointment/', appointmentViewPatient.as_view(), name='api_patient_appointment'),
    path('appointment/<int:pk>/', appointmentViewPatient.as_view(), name='api_patient_appointment_detail'),
    path('appointment/<int:pk>/feedback/', FeedbackView.as_view(), name='api_patient_feedback'),
    path('upcoming-appointment/', upcomingAppointmentView.as_view(), name='api_patient_upcoming-appointment'),
    path('upcoming-appointment/<int:pk>', upcomingAppointmentView.as_view(), name='api_patient_upcoming-appointment_detail'),
    path('previous-appointment/', previousAppointmentView.as_view(), name='api_patient_previous-appointment'),
    path('previous-appointment/<int:pk>', previousAppointmentView.as_view(), name='api_patient_previous-appointment_detail'),
    path('test-report/', TestReportView.as_view(), name='api_patient_test_Report'),
    path('test-report/<int:pk>', TestReportView.as_view(), name='api_patient_test_Report_detail'),
    path('history/', patientHistoryView.as_view(), name='api_patient_history'),
]