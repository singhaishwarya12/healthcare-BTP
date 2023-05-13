from django.urls import path
from .views import DiseaseInfoView, DiseasePredictionView

urlpatterns = [
    path('predict-disease/' , DiseasePredictionView.as_view()),
    path('disease_info/' , DiseaseInfoView.as_view()),
]