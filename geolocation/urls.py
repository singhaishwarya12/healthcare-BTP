from django.urls import path
from .views import GeolocationView
urlpatterns = [
    path('patient/<int:pk>/',GeolocationView.as_view())
]