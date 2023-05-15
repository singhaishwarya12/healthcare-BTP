from rest_framework.views import APIView
from patient.serializers import PrescriptionSerializerPatient, patientHistorySerializer, TestReportSerializer, FeedbackSerializer, \
appointmentHistory
from .serializers import doctorRegistrationSerializer, doctorProfileSerializer, doctorAppointmentSerializer, \
    SlotSerializer, doctorUpAppointmentSerializer, FeedbackDrSerializer, PatientProfileSerializer, DrPrevAppointment
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
from django.db.models import Q
import jwt
import requests

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
        filter = Q(appointment_date__gt=date.today()) | \
         (Q(appointment_date=date.today()) & Q(appointment_time__gte=datetime.now().time()))

        appointment=Appointment.objects.filter(filter).filter(status='new',doctor=user_doctor)
        appointmentSerializer=doctorAppointmentSerializer(appointment, many=True)
        return Response(appointmentSerializer.data, status=status.HTTP_200_OK)

class doctorPrevAppointment(APIView):

    permission_classes = [IsDoctor]

    def get_object(self, pk):
        try:
            return Appointment.objects.get(pk=pk)
        except Appointment.DoesNotExist:
            raise Http404

    def get(self, request,pk=None, format=None):
        user = request.user
        dr = doctor.objects.filter(user=user).get()
        if pk:
            appointment_detail = self.get_object(pk)
            app_serializer = DrPrevAppointment(appointment_detail)
            return Response(app_serializer.data, status=status.HTTP_200_OK)
        
        filter = Q(appointment_date__lt=date.today()) | \
         (Q(appointment_date=date.today()) & Q(appointment_time__lte=datetime.now().time()))

        """appointment=Appointment.objects.filter(Q(status='confirmed'), 
                                               patient=user_patient, appointment_date__lt=date.today())"""
        appointment=Appointment.objects.filter(filter).filter(status='confirmed',doctor=dr)
        serializer=DrPrevAppointment(appointment, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


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
            app_serializer = doctorUpAppointmentSerializer(appointment)
            return Response(app_serializer.data, status=status.HTTP_200_OK)
        filter = Q(appointment_date__gt=date.today()) | \
         (Q(appointment_date=date.today()) & Q(appointment_time__gte=datetime.now().time()))

        appointment=Appointment.objects.filter(filter).filter(status='confirmed',doctor=user_doctor)
        appointmentSerializer=doctorUpAppointmentSerializer(appointment, many=True)
        return Response(appointmentSerializer.data, status=status.HTTP_200_OK)
    
    def generate_meeting_link(self,purpose,dateTime,duration):
        # purpose = request.POST.get('pur')
        # function
        # dateTime = request.POST.get('datetime')
        dateTime=dateTime.strftime("%Y-%m-%dT%H:%M:%SZ") 
        print("dateTime recieved: ",dateTime)
        time_now = datetime.now()
        expiration_time = time_now + timedelta(minutes=2)
        round_of_exp_time = round(expiration_time.timestamp())
        headers ={"alg": "HS256", "typ": "JWT"}
        payload = {"iss": "6MFQvHrLQFSBYa23Q2p2Rg", "exp": round_of_exp_time }
        encoded_jwt = jwt.encode(payload , "VAGUsW3dt4hIdDDUQ2uXc1mayyHhQcCfWmv9" , algorithm = "HS256")
        email = "jinendra09032002@gmail.com"
        url = "https://api.zoom.us/v2/users/me/meetings"
        # dateTime = datetime.datetime(2023, 5, 14, 5, 15).strftime("%Y-%m-%dT%H:%M:%SZ") 
        obj = {
                "topic":purpose ,
                "starttime" : dateTime, 
                "duration" :duration,
                "settings": {
                    'join_before_host': True,
                    'mute_upon_entry': True,
                    'host_video': True,
                    'participant_video': True,
                    'audio': 'both',
                    'auto_recording': 'none',
                    'waiting_room': False,
                },
            }
        header = {"authorization" : "Bearer {}".format(encoded_jwt) , "Content-Type": "application/json"}
        params = {'user_id': email, # use email2's account ID
        }
        response = requests.post(url,json=obj,headers=header,params=params)
        print("response code: ",response.status_code)
        meeting_json = response.json()
        print("type of response: ",type(response))
        print(meeting_json)
        Link = meeting_json['join_url'] 
        print("meeting link: ",Link)
        return Link

    def put(self, request,pk=None, format=None):
        appstatus = request.data['status']
        appointment = self.get_object(pk)
        app_serializer = doctorAppointmentSerializer(instance = appointment, data=request.data,partial=True)
        if app_serializer.is_valid():
            app_serializer.save()
            time = request.data['appointment_time']
            date = request.data['appointment_date']
            start_datetime = datetime.strptime(time, '%H:%M:%S').time()
            date = datetime.strptime(date, '%Y-%m-%d').date()
            slot_date = Dates.objects.filter(doctor_id=appointment.doctor, date=date).get()
            if appstatus == 'confirmed':
                slot_time = Slot.objects.filter(date=slot_date, time=start_datetime).update(isBooked=True)
            else :
                slot_time = Slot.objects.filter(date=slot_date, time=start_datetime).update(isBooked=False)
                #work on it description textfield in request.data!
                """purpose=request.data['purpose']
                dateTime=datetime.combine(date,start_datetime)
                duration=request.data['duration']
                meetingLink = self.generate_meeting_link(purpose,dateTime,duration)
                app_serializer = doctorAppointmentSerializer(instance = appointment, data=str(meetingLink),partial=True)
                app_serializer.save()"""

            return Response(app_serializer.data, status=status.HTTP_200_OK)
        
        return Response(app_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class FeedbackView(APIView):

    def get(self, request, format=None):
        dr = doctor.objects.get(user=request.user)
        feedback = Feedback.objects.filter(dr=dr)
        serializer = FeedbackSerializer(feedback, many=True)
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
                dosage=m['dosage'],
                With=m['With']
            )
        serializer = PrescriptionSerializerPatient(prescription)
        if serializer.is_valid :
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class PatientProfileView(APIView):
    permission_classes = [IsDoctor]

    def get(self, request,pk=None, format = None):
        a = Appointment.objects.get(pk=request.data['appointment'])
        history = TreatmentHistory.objects.filter(patient=a.patient)
        dr = doctor.objects.get(user=request.user)
        list_of_appointments = []
        #print(request.data['appointment'])
        
        profile_serializer = PatientProfileSerializer(a.patient)
        list = AllowedAppointments.objects.filter(patient=a.patient,allowing_appointment=a)
        for h in list:
            appointment = Appointment.objects.get(pk=h.allowed)
            history_serializer = appointmentHistory(appointment)
            list_of_appointments.append(history_serializer.data)


        #history_serializer = RestrictedHistorySerializer(history, many=True)
        test_report = TestReport.objects.filter(patient=a.patient)
        test_report_serializer = TestReportSerializer(test_report,many=True)
        return Response({
            'patient_profile': profile_serializer.data,
            #'patient_history': history_serializer.data,
            'patient_history': list_of_appointments,
            'test_report':test_report_serializer.data
        }, status=status.HTTP_200_OK)