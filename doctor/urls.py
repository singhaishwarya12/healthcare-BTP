from .views import registrationView, CustomAuthToken, doctorProfileView, doctorAppointmentView, FeedbackView, WritePrescription, \
                PatientProfileView, doctorPendingRequestView, doctorPrevAppointment
from django.urls import path

urlpatterns = [
    path('signup/', registrationView.as_view(), name='api_doctor_registration'),
    path('login/', CustomAuthToken.as_view(), name='api_doctor_login'),
    path('profile/', doctorProfileView.as_view(), name='api_doctor_profile'),
    #to view pending appointments and either approve them or cancel them
    path('appointment/pending-requests/',doctorPendingRequestView.as_view()),
    #to show list of upcoming approved appointments
    path('appointment/', doctorAppointmentView.as_view(), name='api_doctor_appointment'),
    path('appointment/<int:pk>/', doctorAppointmentView.as_view(), name='api_doctor_appointment_detail'),
    #for confirmed previous appointment
    path('previous-appointment/',doctorPrevAppointment.as_view()),
    path('appointment/<int:pk>/prescription/',WritePrescription.as_view()),
    path('feedback/', FeedbackView.as_view(), name='api_doctor_feedback'),
    #path('appointment/<int:pk>/feedback/', FeedbackView.as_view(), name='api_doctor_feedback'),
    path('patient/profile/',PatientProfileView.as_view())
]