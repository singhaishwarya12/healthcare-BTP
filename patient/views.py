from rest_framework.views import APIView
from .serializers import (patientRegistrationSerializer,
                          patientProfileSerializer,
                          appointmentSerializerPatient,
                          FeedbackSerializer,
                          TestReportSerializer)
from doctor.serializers import doctorAppointmentSerializer, SlotSerializer, SlotTimeSerializer

from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers, status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.permissions import BasePermission
from .models import patient, Appointment, TestReport, Feedback
from doctor.models import doctor, Dates, Slot
from django.db.models import Q
from datetime import date, time, datetime

class IsPatient(BasePermission):
    """custom Permission class for Patient"""

    def has_permission(self, request, view):
        return bool(request.user and request.user.groups.filter(name='patient').exists())
        
class CustomAuthToken(ObtainAuthToken):

    """This class returns custom Authentication token only for patient"""

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        account_approval = user.groups.filter(name='patient').exists()
        if account_approval==False:
            return Response(
                {
                    'message': "You are not authorised to login as a patient"
                },
                status=status.HTTP_403_FORBIDDEN
            )
        else:
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key
            },status=status.HTTP_200_OK)


class registrationView(APIView):
    """"API endpoint for Patient Registration"""

    permission_classes = []

    def post(self, request, format=None):
        registrationSerializer = patientRegistrationSerializer(
            data=request.data.get('user_data'))
        profileSerializer = patientProfileSerializer(
            data=request.data.get('profile_data'))
        checkregistration = registrationSerializer.is_valid()
        checkprofile = profileSerializer.is_valid()
        if checkregistration and checkprofile:
            patient = registrationSerializer.save()
            profileSerializer.save(user=patient)
            return Response({
                'user_data': registrationSerializer.data,
                'profile_data': profileSerializer.data
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'user_data': registrationSerializer.errors,
                'profile_data': profileSerializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)



class patientProfileView(APIView):
    """"API endpoint for Patient profile view/update-- Only accessble by patients"""
    permission_classes = [IsPatient]


    def get(self, request, format=None):
        user = request.user
        profile = patient.objects.filter(user=user).get()
        userSerializer=patientRegistrationSerializer(user)
        profileSerializer = patientProfileSerializer(profile)
        return Response({
            'user_data':userSerializer.data,
            'profile_data':profileSerializer.data

        }, status=status.HTTP_200_OK)

    def put(self, request, format=None):
        user = request.user
        profile = patient.objects.filter(user=user).get()
        profileSerializer = patientProfileSerializer(
            instance=profile, data=request.data.get('profile_data'), partial=True)
        if profileSerializer.is_valid():
            profileSerializer.save()
            return Response({
                'profile_data':profileSerializer.data
            }, status=status.HTTP_200_OK)
        return Response({
                'profile_data':profileSerializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

            

class patientHistoryView(APIView):

    """"API endpoint for Patient history- Only accessble by patients"""
    permission_classes = [IsPatient]

    def get(self, request, format=None):
        user = request.user
        user_patient = patient.objects.filter(user=user).get()
        history = patient_history.objects.filter(patient=user_patient)
        historySerializer=patientHistorySerializer(history, many=True)
        return Response(historySerializer.data, status=status.HTTP_200_OK)


class appointmentViewPatient(APIView):
    """"API endpoint for getting appointments details, creating appointment"""
    permission_classes = [IsPatient]

    def get_object(self, pk, user_patient):
        try:
            return Appointment.objects.get(pk=pk, patient=user_patient)
        except Appointment.DoesNotExist:
            raise Http404

    def get(self, request,pk=None, format=None):
        user = request.user
        user_patient = patient.objects.filter(user=user).get()
        
        if pk:
            appointment_detail = self.get_object(pk, user_patient)
            serializer = appointmentSerializerPatient(appointment_detail)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        appointment=Appointment.objects.filter(status='new', patient=user_patient)
        serializer=appointmentSerializerPatient(appointment, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    #to create an appointment
    def post(self, request, format=None):
        """user = request.user
        user_patient = patient.objects.filter(user=user).get()
        appointment_info = request.data.get('appointment_info')
        serializer = appointmentSerializerPatient(
            data=appointment_info)
        if serializer.is_valid():
            serializer.save(patient=user_patient)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response( serializer.errors
        , status=status.HTTP_400_BAD_REQUEST)"""
        user = request.user
        user_patient = patient.objects.filter(user=user).get()

        appointment_info = request.data.get('appointment_info')
        slot_info = request.data.get('slot_info')

        request_time = appointment_info.get('appointment_time')
        start_datetime = datetime.strptime(request_time, '%H:%M:%S').time()
        request_doctor = int(appointment_info.get('doctor'))
        request_date = appointment_info.get('appointment_date')
        date = datetime.strptime(request_date, '%Y-%m-%d').date()

        r_doctor = doctor.objects.get(pk=request_doctor)
        time_slots = Dates.objects.filter(doctor_id=r_doctor, date=date)

        appointment_serializer = appointmentSerializerPatient(data=appointment_info)

        if appointment_serializer.is_valid():
            appointment_serializer.save(patient=user_patient)
            if 'slot_info' in request.data :
                print('request time: '+request_time)
                for slot in time_slots:
                    print("time "+slot.slots.time.strftime('%H:%M') +"\n isBooked = "+str(slot.slots.isBooked))
                    if(slot.slots.time==start_datetime and slot.slots.isBooked==False):
                        print("Match found!")
                        user_doctor = doctor.objects.get(pk=request_doctor)
                        slot = Slot.objects.filter(time=start_datetime).update(isBooked=True)
                        new_slot = Dates.objects.filter(date=date, doctor_id=user_doctor).update(slots=slot)
                        #slot_serializer = SlotSerializer(new_slot)
                        appointment_serializer.save(patient=user_patient)
                        """if slot_serializer.is_valid():
                            #appointment_serializer.save(patient=user_patient)
                            slot_serializer.save()"""
                        return Response({
                                'appointment_data': appointment_serializer.data,
                                #'slot_data' : slot_serializer.data
                                }, status=status.HTTP_201_CREATED)
                    
            return Response(appointment_serializer.data, status=status.HTTP_200_OK)
            """slot_serializer = SlotSerializer(date=request_date,assigned_doctor= r_doctor,slots = slot.slots)
                    if slot_serializer.is_valid():
                        appointment_serializer.save(patient=user_patient)
                        slot_serializer.save(assigned_doctor= r_doctor, slots = slot.slots)
                        return Response(appointment_serializer.data, status=status.HTTP_201_CREATED)"""
        return Response( appointment_serializer.errors
        , status=status.HTTP_400_BAD_REQUEST)

class FeedbackView(APIView):

    def post(self, request,pk=None, format=None):
        appointment = Appointment.objects.get(pk=pk)
        rating = request.data.get('rating')
        comment = request.data.get('comment')

        feedback = Feedback.objects.create(rating=rating, comment=comment,appointment=appointment,given=True)

        serializer = FeedbackSerializer(feedback)
        if serializer.is_valid :
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class upcomingAppointmentView(APIView):

    permission_classes = [IsPatient]

    def get_object(self, pk):
        try:
            return Appointment.objects.get(pk=pk)
        except Appointment.DoesNotExist:
            raise Http404

    def get(self, request,pk=None, format=None):
        user = request.user
        user_patient = patient.objects.filter(user=user).get()
        if pk:
            appointment_detail = self.get_object(pk)
            serializer = appointmentSerializerPatient(appointment_detail)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        appointment=Appointment.objects.filter(status='new', 
                                               patient=user_patient, appointment_date__gte=date.today())
        serializer=appointmentSerializerPatient(appointment, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class previousAppointmentView(APIView):

    permission_classes = [IsPatient]

    def get_object(self, pk):
        try:
            return Appointment.objects.get(pk=pk)
        except Appointment.DoesNotExist:
            raise Http404

    def get(self, request,pk=None, format=None):
        user = request.user
        user_patient = patient.objects.filter(user=user).get()
        if pk:
            appointment_detail = self.get_object(pk)
            serializer = appointmentSerializerPatient(appointment_detail)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        appointment=Appointment.objects.filter(Q(status='new'), 
                                               patient=user_patient, appointment_date__lt=date.today())
        serializer=appointmentSerializerPatient(appointment, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class TestReportView(APIView):

    permission_classes = [IsPatient]

    def get_object(self, pk):
        try:
            return TestReport.objects.get(pk=pk)
        except TestReport.DoesNotExist:
            raise Http404
    
    def get(self, request, pk=None, format=None):
        if pk:
            report_detail = self.get_object(pk)
            serializer = TestReportSerializer(report_detail)
            return Response(serializer.data, status=status.HTTP_200_OK)
        user = request.user
        user_patient = patient.objects.filter(user=user).get()
        serializer=TestReportSerializer(patient=user_patient, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request, format=None):
        user = request.user
        user_patient = patient.objects.filter(user=user).get()
        serializer = TestReportSerializer(
            data=request.data)
        if serializer.is_valid():
            serializer.save(patient=user_patient)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response( serializer.errors
        , status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, pk=None, format=None):
        if pk:
            report_detail = self.get_object(pk)
            serializer = TestReportSerializer(report_detail, data=request.data.get(), partial=True)
        else :
            user = request.user
            user_patient = patient.objects.filter(user=user).get()
            serializer = TestReportSerializer(
                instance=user_patient, data=request.data.get(), partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
