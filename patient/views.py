from rest_framework.views import APIView
from .serializers import (patientRegistrationSerializer,
                          patientProfileSerializer,
                          appointmentSerializerPatient,
                          patientHistorySerializer,
                          FeedbackSerializer,
                          PrescriptionSerializerPatient,
                          TestReportSerializer,
                          appointmentHistory,
                          ViewDrSerializer,
                          pendingReqSerializer)
from doctor.serializers import doctorAppointmentSerializer, SlotSerializer, SlotTimeSerializer

from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers, status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.permissions import BasePermission
from .models import patient, Appointment, TestReport, Feedback, Prescription, Medicine, TreatmentHistory, AllowedAppointments
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
        history = TreatmentHistory.objects.filter(patient=user_patient)
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

        appointment_serializer = appointmentSerializerPatient(data=request.data)

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
                return Response(status=status.HTTP_400_BAD_REQUEST)
            return Response(appointment_serializer.data, status=status.HTTP_200_OK)
        return Response( appointment_serializer.errors
        , status=status.HTTP_400_BAD_REQUEST)

class FeedbackView(APIView):

    def get(self, request,pk=None, format = None):
        appointment = Appointment.objects.get(pk=pk)
        feedback = Feedback.objects.get(appointment=appointment)
        serializer = FeedbackSerializer(feedback)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request,pk=None, format=None):
        appointment = Appointment.objects.get(pk=pk)
        rating = request.data.get('rating')
        comment = request.data.get('comment')
        dr= appointment.doctor

        feedback = Feedback.objects.create(rating=rating, comment=comment,appointment=appointment,dr=dr,given=True)

        serializer = FeedbackSerializer(feedback)
        if serializer.is_valid :
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class patientPendingRequestView(APIView):
    permission_classes = [IsPatient]

    def get_object(self, pk):
        try:
            return Appointment.objects.get(pk=pk)
        except Appointment.DoesNotExist:
            raise Http404

    def get(self, request, pk=None,format=None):
        user = request.user
        user_patient = patient.objects.filter(user=user).get()
        if pk:
            appointment = self.get_object(pk)
            app_serializer = pendingReqSerializer(appointment)
            return Response(app_serializer.data, status=status.HTTP_200_OK)
        filter = Q(appointment_date__gt=date.today()) | \
         (Q(appointment_date=date.today()) & Q(appointment_time__gte=datetime.now().time()))
        
        appointment=Appointment.objects.filter(filter).filter(status='new',patient=user_patient)
        appointmentSerializer=pendingReqSerializer(appointment, many=True)
        return Response(appointmentSerializer.data, status=status.HTTP_200_OK)
    

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
        
        filter = Q(appointment_date__gt=date.today()) | \
         (Q(appointment_date=date.today()) & Q(appointment_time__gte=datetime.now().time()))
        
        appointment=Appointment.objects.filter(filter).filter(status='confirmed',patient=user_patient)
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
            presciption = Prescription.objects.get(appointment=appointment_detail)
            #presciption_serializer = PrescriptionSerializerPatient(presciption)
            app_serializer = appointmentHistory(appointment_detail)
            return Response(app_serializer.data, status=status.HTTP_200_OK)
        
        filter = Q(appointment_date__lt=date.today()) | \
         (Q(appointment_date=date.today()) & Q(appointment_time__lte=datetime.now().time()))

        """appointment=Appointment.objects.filter(Q(status='confirmed'), 
                                               patient=user_patient, appointment_date__lt=date.today())"""
        appointment=Appointment.objects.filter(filter).filter(status='confirmed',patient=user_patient)
        serializer=appointmentHistory(appointment, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class SlotView(APIView):

    permission_classes = [IsPatient]
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
        testreport = TestReport.objects.filter(patient=user_patient)
        serializer=TestReportSerializer(testreport, many=True)
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
            data = request.data.pop('id')
            serializer = TestReportSerializer(report_detail, data=data, partial=True)
        else :
            user = request.user
            user_patient = patient.objects.filter(user=user).get()
            id = request.data.get('id')
            data = request.data
            report = TestReport.objects.get(patient=user_patient,id=id)
            serializer = TestReportSerializer(
                report, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PrescriptionView(APIView):

    permission_classes = [IsPatient]

    def get_object(self, pk):
        try:
            return Prescription.objects.get(pk=pk)
        except Prescription.DoesNotExist:
            raise Http404

    def get(self, request,pk=None, format=None):
        user = request.user
        user_patient = patient.objects.filter(user=user).get()
        if pk:
            prescription_detail = self.get_object(pk)
            serializer = PrescriptionSerializerPatient(prescription_detail)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        prescription=Prescription.objects.filter(Patient=user_patient)
        serializer=PrescriptionSerializerPatient(prescription, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class GetDrView(APIView):
    permission_classes = [IsPatient]

    def get_object(self, pk):
        try:
            return doctor.objects.get(pk=pk)
        except doctor.DoesNotExist:
            raise Http404
    
    def get(self, request, pk=None, format=None):
        if pk:
            dr_detail = self.get_object(pk)
            serializer = ViewDrSerializer(dr_detail)
            return Response(serializer.data, status=status.HTTP_200_OK)
        list = doctor.objects.all().order_by('user__first_name')
        serializer=ViewDrSerializer(list, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class DrFeedbackView(APIView):
    permission_classes = [IsPatient]

    def get(self, request, pk=None, format=None):
        dr = doctor.objects.get(pk=pk)
        feedback = Feedback.objects.filter(dr=dr)
        serializer = FeedbackSerializer(feedback, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
class SlotView2(APIView):

    permission_classes = [IsPatient]

    def get(self, request, format = None):
        fid = request.GET.get('doctor') #request should contain doctor
        user_doctor = doctor.objects.get(pk=fid)
        date = request.GET.get('date')

        try: 
            date_slots = Dates.objects.filter(doctor_id=user_doctor, date=date).get()
        except Dates.DoesNotExist:
            date_slots = Dates.objects.create(doctor_id=user_doctor, date=date)

        #try: 
        time_slots = Slot.objects.filter(date=date_slots)
        #except Slot.DoesNotExist:
        if len(time_slots)==0 :
            times = [9,12,14,17]
            for t in times:
                slotTime = time(t)
                s = Slot.objects.create(time=slotTime, isBooked=False, date=date_slots)
        

        """if not time_slots.exists():
            times = [9,12,14,17]
            for t in times:
                slotTime = time(t)
                s = Slot.objects.create(time=slotTime, isBooked=False, date=date_slots)"""

        slots = Slot.objects.filter(Q(date=date_slots) & Q(isBooked=False))
        serializer = SlotTimeSerializer(slots, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class appointmentViewPatient2(APIView):
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
        
        appointment=Appointment.objects.filter(patient=user_patient)
        serializer=appointmentSerializerPatient(appointment, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    #to create an appointment
    def post(self, request,pk=None, format=None):
        user = request.user
        user_patient = patient.objects.filter(user=user).get()

        time = request.data['appointment_time']
        date = request.data['appointment_date']
        #dr = request.data['doctor']

        start_datetime = datetime.strptime(time, '%H:%M:%S').time()
        #dr = int(dr)
        date = datetime.strptime(date, '%Y-%m-%d').date()

        r_doctor = doctor.objects.get(pk=pk)
        #slot_date = Dates.objects.filter(doctor_id=r_doctor, date=date).get()
        #slot_time = Slot.objects.filter(date=slot_date, time=start_datetime).update(isBooked=True)

        request.data['doctor']=pk

        if TreatmentHistory.objects.filter(patient=user_patient, doctor=r_doctor).exists():
            treatment_history = TreatmentHistory.objects.filter(patient=user_patient, doctor=r_doctor).get()
        else :
            treatment_history = TreatmentHistory.objects.create(patient=user_patient, doctor=r_doctor)

        appointment = Appointment.objects.create(patient=user_patient,
                                                doctor=r_doctor,
                                                symptoms=request.data['symptoms'],
                                                appointment_date = date,
                                                appointment_time = time,
                                                treatment_history=treatment_history
                                                )
        for a in request.data['allowed_ids']:
            print(a)
            allow = AllowedAppointments.objects.create(patient=user_patient,
                                                       allowing_appointment=appointment,
                                                       allowed=a)

        return Response(status=status.HTTP_201_CREATED)

class DoctorSearchView(APIView):
    def get(self, request):
        filter = request.data['filter']
        search_query = request.query_params.get('search', '')
        if filter == 'specialization':
            doctors = doctor.objects.filter(specialization__istartswith=search_query)
        else :
            doctors =   doctor.objects.filter(user__first_name__istartswith=search_query) | \
                        doctor.objects.filter(user__last_name__istartswith=search_query)
        if len(doctors)==0:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        serializer = ViewDrSerializer(doctors, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
