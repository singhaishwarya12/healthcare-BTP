from django.db.models import fields
from django.db.models.query import QuerySet
from rest_framework import serializers
from user.models import User
from patient.models import patient, Appointment, TestReport, Feedback, Medicine, Prescription, TreatmentHistory
from django.contrib.auth.models import Group
from doctor.models import doctor
from doctor.serializers import FeedbackDrSerializer
from datetime import date, datetime, time


class patientRegistrationSerializer(serializers.Serializer):

    username=serializers.CharField(label='Username:')
    first_name=serializers.CharField(label='First name:')
    last_name=serializers.CharField(label='Last name:', required=False)
    password = serializers.CharField(label='Password:',style={'input_type': 'password'}, write_only=True,min_length=8,
    help_text="Your password must contain at least 8 characters and should not be entirely numeric."
    )
    password2=serializers.CharField(label='Confirm password:',style={'input_type': 'password'},  write_only=True)
    

    
    def validate_username(self, username):
        username_exists=User.objects.filter(username__iexact=username)
        if username_exists:
            raise serializers.ValidationError({'username':'This username already exists'})
        return username

        
    def validate_password(self, password):
        if password.isdigit():
            raise serializers.ValidationError('Your password should contain letters!')
        return password  

 

    def validate(self, data):
        password=data.get('password')
        password2=data.pop('password2')
        if password != password2:
            raise serializers.ValidationError({'password':'password must match'})
        return data


    def create(self, validated_data):
        user= User.objects.create(
                username=validated_data['username'],
                first_name=validated_data['first_name'],
                last_name=validated_data['last_name'],
                status=False
            )
        user.set_password(validated_data['password'])
        user.save()
        group_patient, created = Group.objects.get_or_create(name='patient')
        group_patient.user_set.add(user)
        return user


class patientProfileSerializer(serializers.Serializer):
    age=serializers.DecimalField(label="Age:", max_digits=4,decimal_places=1)
    address= serializers.CharField(label="Address:")
    pincode = serializers.CharField()
    mobile=serializers.CharField(label="Mobile Number:", max_length=20)
    pic = serializers.ImageField(required=False)
    email = serializers.EmailField(label="Email: ")
    gender = serializers.CharField()

    def validate_mobile(self, mobile):
        if mobile.isdigit()==False:
            raise serializers.ValidationError('Please Enter a valid mobile number!')
        return mobile
    
    def create(self, validated_data):
        try:
            new_patient= patient.objects.create(
                age=validated_data['age'],
                pic = validated_data['pic'],
                address=validated_data['address'],
                pincode=validated_data['pincode'],
                mobile=validated_data['mobile'],
                email=validated_data['email'],
                user=validated_data['user'],
                gender = validated_data['gender']
            )
        except KeyError:
            new_patient= patient.objects.create(
                age=validated_data['age'],
                address=validated_data['address'],
                pincode=validated_data['pincode'],
                mobile=validated_data['mobile'],
                email=validated_data['email'],
                user=validated_data['user'],
                gender = validated_data['gender']
            )
        return new_patient
    
    def update(self, instance, validated_data):
        instance.age=validated_data.get('age', instance.age)
        instance.pic=validated_data.get('pic', instance.pic)
        instance.address=validated_data.get('address', instance.address)
        instance.pincode=validated_data.get('pincode', instance.pincode)
        instance.mobile=validated_data.get('mobile', instance.mobile)
        instance.email=validated_data.get('email', instance.email)
        instance.save()
        return instance

class patientAccountSerializer(serializers.Serializer):
    id=serializers.UUIDField(read_only=True)
    username=serializers.CharField(label='Username:', read_only=True)
    first_name=serializers.CharField(label='First name:')
    last_name=serializers.CharField(label='Last name:', required=False)
    status=serializers.BooleanField(label='status')
    patient=patientProfileSerializer(label='User')


    def update(self, instance, validated_data):
        try:
            patient_profile=validated_data.pop('patient')
        except:
            raise serializers.ValidationError("Please enter data related to patient's profile")

        profile_data=instance.patient

        instance.first_name=validated_data.get('first_name', instance.first_name)
        instance.last_name=validated_data.get('last_name', instance.last_name)
        instance.status=validated_data.get('status', instance.status)
        instance.save()

        profile_data.age=patient_profile.get('age', profile_data.age)
        profile_data.address=patient_profile.get('address', profile_data.address)
        profile_data.mobile=patient_profile.get('mobile', profile_data.mobile)
        profile_data.save()

        return instance


class appointmentSerializerPatient(serializers.Serializer):
    status_choice = (
        ('new', 'New'),
        ('confirmed', 'confirmed'),
        ('cancelled', 'cancelled'),
        ('completed', 'completed')
    )
    id=serializers.PrimaryKeyRelatedField(read_only=True)
    appointment_date = serializers.DateField(label='Appointment date')
    appointment_time = serializers.TimeField(label='Appointement time')
    status = serializers.ChoiceField(choices=status_choice, default='new')
    dr_name=serializers.SerializerMethodField('related_dr_name')
    meeting_link = serializers.CharField(max_length = 100, required= False)
    symptoms = serializers.CharField(max_length=200)

    def related_dr_name(self, obj):
        return obj.doctor.get_name

    def create(self,validated_data):
        patient=validated_data['patient']
        dr=validated_data['doctor']
        dr = doctor.objects.get(pk=dr)

        if TreatmentHistory.objects.filter(patient=patient, doctor=dr).exists():
            treatment_history = TreatmentHistory.objects.filter(patient=patient, doctor=dr).get()
        else :
            treatment_history = TreatmentHistory.objects.create(patient=patient, doctor=dr)
        
        new_appointment= Appointment.objects.create(
            treatment_history = treatment_history,
            appointment_date=validated_data['appointment_date'],
            appointment_time=validated_data['appointment_time'],
            patient=patient,
            doctor=dr,
            symptoms = validated_data['symptoms']
        )
        return new_appointment


class FeedbackSerializer(serializers.Serializer):
    rating = serializers.IntegerField()
    #given = serializers.BooleanField()
    comment = serializers.CharField(max_length=200)
    class Meta:
        model = Feedback
        fields = '__all__'  

class TestReportSerializer(serializers.Serializer):
    id=serializers.PrimaryKeyRelatedField(read_only=True)
    test_name = serializers.CharField(max_length = 20)
    test_date = serializers.DateField(label='Test date')
    report = serializers.FileField(max_length=None, required=False)
    dr = serializers.CharField()

    def create(self, validated_data):
        new_report = TestReport.objects.create(
            patient = validated_data['patient'],
            test_name = validated_data['test_name'],
            test_date = validated_data['test_date'],
            report = validated_data.get('report'),
            dr = validated_data['dr']
        )
        return new_report
    
    def update(self, instance, validated_data):
        instance.test_name=validated_data.get('test_name', instance.test_name)
        instance.test_date=validated_data.get('test_date', instance.test_date)
        instance.save()
        return instance

class medicineSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=200)
    type = serializers.CharField(max_length=10)
    duration = serializers.CharField(max_length=200)
    times = serializers.CharField(max_length=200)
    dosage = serializers.CharField(max_length=200)
    With = serializers.CharField(max_length=200)

class PrescriptionSerializerPatient(serializers.Serializer):
    diagnosis = serializers.CharField()
    medicine = medicineSerializer(many=True)
    advice = serializers.CharField()
    test_required = serializers.CharField()

class PdfSerializer(serializers.Serializer):
    diagnosis = serializers.CharField()
    medicine = medicineSerializer(many=True)
    advice = serializers.CharField()
    test_required = serializers.CharField()
    clinic_name = serializers.SerializerMethodField('get_clinic_name')
    dr_name = serializers.SerializerMethodField('get_dr_name')
    patient_name = serializers.SerializerMethodField('get_patient_name')
    patient_age = serializers.SerializerMethodField('get_age')
    patient_gender = serializers.SerializerMethodField('get_gender')
    symptoms = serializers.SerializerMethodField('get_symptoms')

    def get_clinic_name(self, obj):
        return obj.Doctor.clinic_name
    
    def get_dr_name(self, obj):
        return obj.Doctor.get_name
    
    def get_patient_name(self, obj):
        return obj.Patient.get_name
    
    def get_age(self, obj):
        return obj.Patient.age
    
    def get_gender(self, obj):
        return obj.Doctor.gender
    
    def get_symptoms(self, obj):
        return obj.appointment.symptoms

class appointmentHistory(serializers.Serializer):
    id=serializers.PrimaryKeyRelatedField(read_only=True)
    doctor = serializers.SerializerMethodField('get_dr_name')
    symptoms = serializers.CharField()
    appointment_date = serializers.DateField()
    appointment_time =serializers.TimeField()
    prescription = PrescriptionSerializerPatient()

    def get_dr_name(self, obj):
        return obj.doctor.get_name
    
class pendingReqSerializer(serializers.Serializer):
    dr_name=serializers.SerializerMethodField('related_dr_name')
    dr_email=serializers.SerializerMethodField('related_dr_email')
    id = serializers.PrimaryKeyRelatedField(read_only=True)
    appointment_date=serializers.DateField(label="Appointment Date:",)
    appointment_time=serializers.TimeField(label="Appointment Time:")
    symptoms = serializers.CharField()

    def related_dr_name(self, obj):
        return obj.doctor.get_name
    
    def related_dr_email(self, obj):
        return obj.doctor.email

class patientHistorySerializer(serializers.Serializer):

   dr_name = serializers.SerializerMethodField('related_doctor_name')
   patient_name = serializers.SerializerMethodField('related_patient_name')
   appointment =  appointmentHistory(many=True)

   def related_doctor_name(self, obj):
        return obj.doctor.get_name
   
   def related_patient_name(self, obj):
        return obj.patient.get_name
   
   def to_representation(self, instance):
        appointment = instance.appointment.filter(status='confirmed',
                                                  appointment_date__lte=date.today()
                                                  )
        app_serializer = appointmentHistory(appointment, many=True)
        representation = super().to_representation(instance)
        representation['appointment'] = app_serializer.data

        return representation

class ViewDrSerializer(serializers.Serializer):
    specialization = serializers.CharField()
    mobile = serializers.CharField()
    address = serializers.CharField()
    pincode = serializers.CharField()
    feesperSession=serializers.CharField()
    registration_num = serializers.IntegerField()
    pic = serializers.ImageField(required=False)
    email = serializers.EmailField(label="Email: ")
    dr_name = serializers.SerializerMethodField('related_doctor_name')
    gender = serializers.CharField()
    feedback = FeedbackDrSerializer(many=True)
    dr_id = serializers.SerializerMethodField('get_dr_id')

    def related_doctor_name(self, obj):
        return obj.get_name
    
    def related_doctor_gender(self, obj):
        return obj.gender

    def get_dr_id(self,obj):
        return obj.id
    
    class Meta:
        ordering = ['get_name']