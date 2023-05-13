from rest_framework.views import APIView
from patient.serializers import PrescriptionSerializerPatient, patientHistorySerializer, TestReportSerializer
from .serializers import doctorRegistrationSerializer, doctorProfileSerializer, doctorAppointmentSerializer, SlotSerializer, SlotTimeSerializer, FeedbackDrSerializer, PatientProfileSerializer
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers, status
from doctor.models import doctor, Dates, Slot
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.permissions import BasePermission
from patient.models import Appointment, Feedback, Prescription, Medicine, patient, TreatmentHistory, TestReport
import datetime
from datetime import time, datetime, date

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

class doctorPendingRequestView(APIView):
    """API endpoint for getting all appointment detail-only accesible by doctor"""
    permission_classes = [IsDoctor]

    def get_object(self, pk):
        try:
            return Appointment.objects.get(pk=pk)
        except Appointment.DoesNotExist:
            raise Http404

    def get(self, request, pk=None,format=None):
        user = request.user
        user_doctor = doctor.objects.filter(user=user).get()
        if pk:
            appointment = self.get_object(pk)
            app_serializer = doctorAppointmentSerializer(appointment)
            return Response(app_serializer.data, status=status.HTTP_200_OK)
        appointments=Appointment.objects.filter(doctor=user_doctor,status='new')
        appointmentSerializer=doctorAppointmentSerializer(appointments, many=True)
        return Response(appointmentSerializer.data, status=status.HTTP_200_OK)

class doctorAppointmentView(APIView):
    """API endpoint for getting all appointment detail-only accesible by doctor"""
    permission_classes = [IsDoctor]

    def get_object(self, pk):
        try:
            return Appointment.objects.get(pk=pk)
        except Appointment.DoesNotExist:
            raise Http404

    def get(self, request, pk=None,format=None):
        user = request.user
        user_doctor = doctor.objects.filter(user=user).get()
        if pk:
            appointment = self.get_object(pk)
            app_serializer = doctorAppointmentSerializer(appointment)
            return Response(app_serializer.data, status=status.HTTP_200_OK)
        #appointments=Appointment.objects.filter(doctor=user_doctor)
        appointments=Appointment.objects.filter(doctor=user_doctor,status='confirmed',appointment_date__gte=date.today())
        appointmentSerializer=doctorAppointmentSerializer(appointments, many=True)
        return Response(appointmentSerializer.data, status=status.HTTP_200_OK)
       
    def put(self, request,pk=None, format=None):
        appstatus = request.data['status']
        appointment = self.get_object(pk)
        app_serializer = doctorAppointmentSerializer(instance = appointment, data=request.data,partial=True)
        if app_serializer.is_valid():
            app_serializer.save()
            if appstatus == 'confirmed':
                time = request.data['appointment_time']
                date = request.data['appointment_date']
                start_datetime = datetime.strptime(time, '%H:%M:%S').time()
                date = datetime.strptime(date, '%Y-%m-%d').date()
                slot_date = Dates.objects.filter(doctor_id=appointment.doctor, date=date).get()
                slot_time = Slot.objects.filter(date=slot_date, time=start_datetime).update(isBooked=True)
            return Response(app_serializer.data, status=status.HTTP_200_OK)
        return Response(app_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class FeedbackView(APIView):

    def get(self, request,pk=None, format = None):
         appointment = Appointment.objects.get(pk=pk)
         serializer = doctorAppointmentSerializer(appointment)
         feedback = Feedback.objects.get(appointment=appointment)
         serializer = FeedbackDrSerializer(feedback)
         return Response(serializer.data, status=status.HTTP_200_OK)

class WritePrescription(APIView):

    permission_classes = [IsDoctor]

    def post(self, request,pk=None, format=None):
        appointment = Appointment.objects.get(pk=pk)
        diagnosis = request.data.get('diagnosis')
        test_required = request.data.get('test_required')
        advice =request.data.get('advice')
        Patient = appointment.patient
        Doctor = appointment.doctor
        medicine = request.data['medicine']

        prescription = Prescription.objects.create(Doctor=Doctor, 
                                                   diagnosis=diagnosis,
                                                   appointment=appointment,
                                                   Patient=Patient,
                                                   advice=advice,
                                                   test_required=test_required)
        for m in medicine:
            med = Medicine.objects.create(
                prescription=prescription,
                name=m['name'],
                type=m['type'],
                duration=m['duration'],
                times=m['times'],
                dosage=m['dosage']
            )
        serializer = PrescriptionSerializerPatient(prescription)
        if serializer.is_valid :
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class PatientProfileView(APIView):
    permission_classes = [IsDoctor]

    def get(self, request,pk=None, format = None):
        Patient = patient.objects.get(pk=pk)
        profile_serializer = PatientProfileSerializer(Patient)
        history = TreatmentHistory.objects.filter(patient=Patient)
        history_serializer = patientHistorySerializer(history, many=True)
        test_report = TestReport.objects.filter(patient=Patient)
        test_report_serializer = TestReportSerializer(test_report,many=True)
        return Response({
            'patient_profile': profile_serializer.data,
            'patient_history': history_serializer.data,
            'test_report':test_report_serializer.data
        }, status=status.HTTP_200_OK)