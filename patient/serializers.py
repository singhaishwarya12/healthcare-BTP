from django.db.models import fields
from django.db.models.query import QuerySet
from rest_framework import serializers
from user.models import User
from patient.models import patient, Appointment, TestReport, Feedback
from django.contrib.auth.models import Group
from doctor.models import doctor



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
    mobile=serializers.CharField(label="Mobile Number:", max_length=20)
    pic = serializers.ImageField(required=False)
    email = serializers.EmailField(label="Email: ")

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
                mobile=validated_data['mobile'],
                email=validated_data['email'],
                user=validated_data['user']
            )
        except KeyError:
            new_patient= patient.objects.create(
                age=validated_data['age'],
                address=validated_data['address'],
                mobile=validated_data['mobile'],
                email=validated_data['email'],
                user=validated_data['user']
            )
        return new_patient
    
    def update(self, instance, validated_data):
        instance.age=validated_data.get('age', instance.age)
        instance.pic=validated_data.get('pic', instance.pic)
        instance.address=validated_data.get('address', instance.address)
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
    id=serializers.IntegerField()
    appointment_date = serializers.DateField(label='Appointment date')
    appointment_time = serializers.TimeField(label='Appointement time')
    status = serializers.ChoiceField(choices=status_choice, default='new')
    doctor = serializers.PrimaryKeyRelatedField(queryset=doctor.objects.all(), required=False)
    meeting_link = serializers.CharField(max_length = 100, required= False)
    symptoms = serializers.CharField(max_length=200)


    def create(self, validated_data):
        new_appointment= Appointment.objects.create(
            patient=validated_data['patient'],
            appointment_date=validated_data['appointment_date'],
            appointment_time=validated_data['appointment_time'],
            doctor=validated_data['doctor'],
            symptoms = validated_data['symptoms']
        )
        return new_appointment


class FeedbackSerializer(serializers.Serializer):
    rating = serializers.IntegerField()
    given = serializers.BooleanField()
    comment = serializers.CharField(max_length=200)
    class Meta:
        model = Feedback
        fields = '__all__'


class patientTreatmentHistorySerializer(serializers.Serializer):
    Surgery = 'S'
    Cardiology = 'C'
    Dermatalogy = 'DT'
    ENT = 'ENT'
    Gynecology = 'G'
    Neurology = 'N'
    Orthopedic = 'OP'
    Pediatric = 'PT'
    Physiotherapy = 'PY'

    treatment_choices = [
        (Surgery, 'Surgery'),
        (Cardiology,'Cardiology'),
        (Dermatalogy, 'Dermatalogy'),
        (ENT, 'ENT'),
        (Gynecology , 'Gynaecology'),
        (Neurology, 'Neurology'),
        (Orthopedic, 'Orthopedic'),
        (Pediatric, 'Pediatric'),
        (Physiotherapy, 'Physiotherapy'),
    ]
    treatment_category = serializers.ChoiceField(label='Category: ', choices=treatment_choices)
    #prescriptions = PrescriptionSerializer()

    """
    admit_date=serializers.DateField(label="Admit Date:", read_only=True)
    symptomps=serializers.CharField(label="Symptomps:", style={'base_template': 'textarea.html'})
    
    #required=False; if this field is not required to be present during deserialization.
    release_date=serializers.DateField(label="Release Date:", required=False)
    assigned_doctor=serializers.StringRelatedField(label='Assigned Doctor:')
    patient_appointments=appointmentSerializerPatient(label="Appointments",many=True)
"""
    #def update()

   

class TestReportSerializer(serializers.Serializer):
    id=serializers.IntegerField(read_only=True)
    testName = serializers.CharField(max_length = 20)
    testDate = serializers.DateField(label='Test date')
    testReport = serializers.FileField(max_length=None)

    def create(self, validated_data):
        new_report = TestReport.object.create(
            testName = validated_data['test_name'],
            testDate = validated_data['test_date'],
            testReport = validated_data['report']
        )
        return new_report
    
    def update(self, instance, validated_data):
        instance.testName=validated_data.get('test_name', instance.testName)
        instance.testDate=validated_data.get('test_date', instance.testDate)
        instance.save()
        return instance