from .views import registrationView, CustomAuthToken, doctorProfileView, doctorAppointmentView, SlotView, FeedbackView
from django.urls import path

urlpatterns = [
    path('signup/', registrationView.as_view(), name='api_doctor_registration'),
    path('login/', CustomAuthToken.as_view(), name='api_doctor_login'),
    path('profile/', doctorProfileView.as_view(), name='api_doctor_profile'),
    path('appointment/', doctorAppointmentView.as_view(), name='api_doctor_profile'),
    path('appointment/<int:pk>/feedback/', FeedbackView.as_view(), name='api_doctor_feedback'),
    path('get-slots/', SlotView.as_view(), name='api_doctor_slots_view')
]