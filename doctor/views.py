from rest_framework.views import APIView
from .serializers import doctorRegistrationSerializer, doctorProfileSerializer, doctorAppointmentSerializer, SlotSerializer, SlotTimeSerializer, FeedbackDrSerializer
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers, status
from doctor.models import doctor, Dates, Slot
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.permissions import BasePermission
from patient.models import Appointment, Feedback
import datetime
from datetime import time

class IsDoctor(BasePermission):
    """custom Permission class for Doctor"""
    def has_permission(self, request, view):
        return bool(request.user and request.user.groups.filter(name='doctor').exists())

class CustomAuthToken(ObtainAuthToken):

    """This class returns custom Authentication token only for Doctor"""

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        account_approval = user.groups.filter(name='doctor').exists()
        if account_approval==False:
            return Response(
                {
                    'message': "You are not authorised to login as a doctor"
                },
                status=status.HTTP_403_FORBIDDEN
            )
        else:
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key
            },status=status.HTTP_200_OK)

class registrationView(APIView):

    """"API endpoint for doctor Registration"""

    permission_classes = []
    def post(self, request, format=None):
        registrationSerializer = doctorRegistrationSerializer(
            data=request.data.get('user_data'))
        profileSerializer = doctorProfileSerializer(
            data=request.data.get('profile_data'))
        checkregistration = registrationSerializer.is_valid()
        checkprofile = profileSerializer.is_valid()
        if checkregistration and checkprofile:
            doctor = registrationSerializer.save()
            profileSerializer.save(user=doctor)
            return Response({
                'user_data': registrationSerializer.data,
                'profile_data': profileSerializer.data
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'user_data': registrationSerializer.errors,
                'profile_data': profileSerializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)





class doctorProfileView(APIView):
    """"API endpoint for doctor profile view/update-- Only accessble by doctors"""

    permission_classes=[IsDoctor]

    def get(self, request, format=None):
        user = request.user
        profile = doctor.objects.filter(user=user).get()
        userSerializer=doctorRegistrationSerializer(user)
        profileSerializer = doctorProfileSerializer(profile)
        return Response({
            'user_data':userSerializer.data,
            'profile_data':profileSerializer.data

        }, status=status.HTTP_200_OK)

    def put(self, request, format=None):
        user = request.user
        profile = doctor.objects.filter(user=user).get()
        profileSerializer = doctorProfileSerializer(
            instance=profile, data=request.data.get('profile_data'), partial=True)
        if profileSerializer.is_valid():
            profileSerializer.save()
            return Response({
                'profile_data':profileSerializer.data
            }, status=status.HTTP_200_OK)
        return Response({
                'profile_data':profileSerializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

class doctorAppointmentView(APIView):
    """API endpoint for getting all appointment detail-only accesible by doctor"""
    permission_classes = [IsDoctor]

    def get(self, request, format=None):
        user = request.user
        user_doctor = doctor.objects.filter(user=user).get()
        appointments=Appointment.objects.filter(doctor=user_doctor)
        appointmentSerializer=doctorAppointmentSerializer(appointments, many=True)
        return Response(appointmentSerializer.data, status=status.HTTP_200_OK)
    
class SlotView(APIView):

    #permission_classes
    """appointments = Appointment.objects.filter(doctor_id=doctor_id, date=date)
        booked_slots = []
        for appointment in appointments:
            booked_slots.append(appointment.slot)
        available_slots = Slot.objects.exclude(id__in=[slot.id for slot in booked_slots])
        serializer = SlotSerializer(available_slots, many=True)"""

    def get(self, request, format = None):
        id = request.data.get('doctor') #request should contain doctor
        user_doctor = doctor.objects.get(pk=id)
        date = request.data.get('date')

        time_slots = Dates.objects.filter(doctor_id=user_doctor, date=date)

        if not time_slots.exists():
            times = [9,12,14,17]
            for t in times:
                slotTime = time(t)
                s = Slot.objects.create(time=slotTime, isBooked=False)
                Dates.objects.create(doctor_id=user_doctor, date=date,slots=s)

        available_slots = []
        for slot in time_slots:
            if(slot.slots.isBooked==False):
                available_slots.append(slot.slots)
        slots = Slot.objects.filter(id__in=[slot.id for slot in available_slots])
        serializer = SlotTimeSerializer(slots, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    """def post(self, request, format=None):
        id = request.user #request should contain doctor
        user_doctor = doctor.objects.filter(user=id).get()
        date = request.data.get('date')
        slots = Dates.objects.filter(doctor_id=user_doctor, date=date).get()
        serializer = SlotSerializer(
            data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response( serializer.errors
        , status=status.HTTP_400_BAD_REQUEST)"""
    

class FeedbackView(APIView):

    def get(self, request,pk=None, format = None):
         appointment = Appointment.objects.get(pk=pk)
         serializer = doctorAppointmentSerializer(appointment)
         feedback = Feedback.objects.get(appointment=appointment)
         serializer = FeedbackDrSerializer(feedback)
         return Response(serializer.data, status=status.HTTP_200_OK)

