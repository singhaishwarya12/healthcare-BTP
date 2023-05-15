from django.shortcuts import render
from twilio.rest import Client
from django.http import HttpResponse
from datetime import datetime
import pytz

from rest_framework.views import APIView
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers, status
from doctor.models import doctor, Dates, Slot
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.permissions import BasePermission
from patient.models import Appointment, Feedback, Prescription, Medicine, patient, TreatmentHistory, TestReport, AllowedAppointments
import datetime
from datetime import time, datetime, date, timedelta
import json

account_sid = 'AC7553f202514a8a162cf09a66cc1bfe4e'
auth_token = '3452a9647b0b055a96ddfec9f15ab852'
msg_service_sid = 'MGad1a64453007027c1f6cc73dff9be8ab'
twilio_number = '+12707135166'


class AlarmView(APIView):

    def createCall(self,request):
        """date =request.POST.get('date')
        time =request.POST.get('time')
        print(date)
        print(time)
        time = datetime.strptime(time, '%H:%M:%S').time()
        date = datetime.strptime(date, '%Y-%m-%d').date()
        dateTime = datetime.combine(date,time)"""
        dateTime = request.data.get('dateTime')
        #dateTime = dateTime.strftime("%Y-%m-%dT%H:%M:%SZ")
        #dateTime = dateTime + ":00Z"
        print("dateTime: ",dateTime)
        send_time = datetime.strptime(dateTime, "%Y-%m-%d %H:%M:%S")
        print("send_time: ",send_time)
        ist_tz = pytz.timezone('Asia/Kolkata')
        utc_tz = pytz.timezone('UTC')
        scheduled_time = ist_tz.localize(send_time).astimezone(utc_tz)
        print("scheduled time: ", scheduled_time)
        phone = request.data.get('phone')
        message = request.data.get('msg')
        phoneno = '+91' + phone
        print(phoneno)

        client = Client(account_sid, auth_token)

        call = client.messages.create(
                body = message,
                send_at=scheduled_time,
                schedule_type='fixed',
                to=phoneno,
                from_=twilio_number,
                messaging_service_sid = msg_service_sid,
            )
        
        data = {'status':'success'}
        json_data = json.dumps(data)
        response = HttpResponse(json_data, content_type='application/json')
        return response
        #return HttpResponse('Call scheduled successfully')

    def post(self, request, format=None):

        h = self.createCall(request)
        return h
        #return Response(h,status=status.HTTP_200_OK)


