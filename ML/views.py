from django.shortcuts import render
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers, status
import numpy as np    
import pandas as pd
import openai
from joblib import load

openai.api_key = settings.OPENAI_API_KEY


model = load('./ML/model.joblib')

features = pd.read_csv("./ML/features.csv")
features = features.drop(["prognosis"],axis=1)
feature_names = features.columns.tolist()


class DiseasePredictionView(APIView):

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

        return Response({
            'disease': predicted_disease,
            'confience_score': confidencescore
            }, status=status.HTTP_200_OK)
   

class DiseaseInfoView(APIView):
     
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
          