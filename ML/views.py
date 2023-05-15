from django.shortcuts import render
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers, status
import numpy as np    
import pandas as pd
import openai
from joblib import load
from doctor.models import doctor
from patient.serializers import ViewDrSerializer
from patient.views import IsPatient

openai.api_key = settings.OPENAI_API_KEY


model = load('./ML/model.joblib')

features = pd.read_csv("./ML/features.csv")
features = features.drop(["prognosis"],axis=1)
feature_names = features.columns.tolist()


class DiseasePredictionView(APIView):
    permission_classes = [IsPatient]

    def post(self, request):
        symptoms = request.data['symptoms']
        X_input = np.zeros((1,132))

        for i in symptoms:
            X_input[0,int(i)] = 1

        df = pd.DataFrame(X_input, columns=feature_names)  
        predicted_disease = model.predict(df)

        y_pred_2 = model.predict_proba(df)
        confidencescore=y_pred_2.max() * 100
        
        confidencescore = format(confidencescore, '.2f')
        print(" confidence score of : = {0} ".format(confidencescore))

        Rheumatologist = [  'Osteoarthristis','Arthritis']
       
        Cardiologist = [ 'Heart attack','Bronchial Asthma','Hypertension ']
       
        ENT_specialist = ['(vertigo) Paroymsal  Positional Vertigo','Hypothyroidism' ]

        Orthopedist = []

        Neurologist = ['Varicose veins','Paralysis (brain hemorrhage)','Migraine','Cervical spondylosis']

        Allergist_Immunologist = ['Allergy','Pneumonia',\
        'AIDS','Common Cold','Tuberculosis','Malaria','Dengue','Typhoid']

        Urologist = [ 'Urinary tract infection','Dimorphic hemmorhoids(piles)']

        Dermatologist = [  'Acne','Chicken pox','Fungal infection','Psoriasis','Impetigo']

        Gastroenterologist = ['Peptic ulcer diseae', 'GERD','Chronic cholestasis','Drug Reaction','Gastroenteritis','Hepatitis E',\
        'Alcoholic hepatitis','Jaundice','hepatitis A',\
         'Hepatitis B', 'Hepatitis C', 'Hepatitis D','Diabetes ','Hypoglycemia']

        if predicted_disease in Rheumatologist :
           consultdoctor = "Rheumatologist"
           
        if predicted_disease in Cardiologist :
           consultdoctor = "Cardiologist"

        elif predicted_disease in ENT_specialist :
           consultdoctor = "ENT specialist"
     
        elif predicted_disease in Orthopedist :
           consultdoctor = "Orthopedist"
     
        elif predicted_disease in Neurologist :
           consultdoctor = "Neurologist"
     
        elif predicted_disease in Allergist_Immunologist :
           consultdoctor = "Allergist/Immunologist"
     
        elif predicted_disease in Urologist :
           consultdoctor = "Urologist"
     
        elif predicted_disease in Dermatologist :
           consultdoctor = "Dermatologist"
     
        elif predicted_disease in Gastroenterologist :
           consultdoctor = "Gastroenterologist"
     
        else :
           consultdoctor = "other"

        if consultdoctor == 'other':
            return Response({
            'disease': predicted_disease,
            'confience_score': confidencescore,
            'dr_info': ""
            }, status=status.HTTP_200_OK)
        
        doctors = doctor.objects.filter(specialization=consultdoctor)
        serializer = ViewDrSerializer(doctors, many=True)

        return Response({
            'disease': predicted_disease,
            'confience_score': confidencescore,
            'dr_info': serializer.data
            }, status=status.HTTP_200_OK)
   

class DiseaseInfoView(APIView):
     
     permission_classes = [IsPatient]
     
     def question(self, q,disease):
        return f'{q}{disease}?'
     
     def post(self,request):
        disease = request.data['disease_name']
        my_disease = str(disease)[1:-1]

        Questions = [
            'What is ',
            'Symptoms of ',
            'Diagnosis for ',
            'Expected Duration of ',
            'Prevention measures for ',
            'Treatment for ',
            'Food to avoid during ',
            'When to call professional during ',
            'Exercise for '
        ]

        information = dict(disease=disease)

        for ques in Questions:
            p = self.question(ques,disease)
            response = openai.Completion.create(
            model="text-davinci-003",
            prompt=p,
            max_tokens=1000,
            n=1,
            stop=None,
            temperature=0.6,
            )
            result = response.choices[0].text
            information[p] = result

        return Response(information, status=status.HTTP_200_OK)
          