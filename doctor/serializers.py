from patient.models import Appointment, Feedback
from rest_framework import serializers
from user.models import User
from doctor.models import doctor, Slot, Dates
from django.contrib.auth.models import Group
from datetime import date, time, datetime

class doctorRegistrationSerializer(serializers.Serializer):

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
        group_doctor, created = Group.objects.get_or_create(name='doctor')
        group_doctor.user_set.add(user)
        return user

class doctorProfileSerializer(serializers.Serializer):
    Surgery = 'S'
    Cardiology = 'C'
    Dermatalogy = 'DT'
    ENT = 'ENT'
    Gynecology = 'G'
    Neurology = 'N'
    Orthopedic = 'OP'
    Pediatric = 'PT'
    Physiotherapy = 'PY'

    department_choice = [
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
    department=serializers.ChoiceField(label='Department:', choices=department_choice)
    address= serializers.CharField(label="Address:")
    mobile=serializers.CharField(label="Mobile Number:", max_length=20)
    pic = serializers.ImageField(required=False)


    def validate_mobile(self, mobile):
        if mobile.isdigit()==False:
            raise serializers.ValidationError('Please Enter a valid mobile number!')
        return mobile
    
    def create(self, validated_data):
        try: 
            new_doctor= doctor.objects.create(
                department=validated_data['department'],
                address=validated_data['address'],
                mobile=validated_data['mobile'],
                pic=validated_data['pic'],
                user=validated_data['user']
            )
        except KeyError:
            new_doctor= doctor.objects.create(
                department=validated_data['department'],
                address=validated_data['address'],
                mobile=validated_data['mobile'],
                user=validated_data['user']
            )
        return new_doctor
    
    def update(self, instance, validated_data):
        instance.department=validated_data.get('department', instance.department)
        instance.address=validated_data.get('address', instance.address)
        instance.mobile=validated_data.get('mobile', instance.mobile)
        instance.save()
        return instance



class patientHistorySerializerDoctorView(serializers.Serializer):
    Cardiologist='CL'
    Dermatologists='DL'
    Emergency_Medicine_Specialists='EMC'
    Immunologists='IL'
    Anesthesiologists='AL'
    Colon_and_Rectal_Surgeons='CRS'
    admit_date=serializers.DateField(label="Admit Date:", read_only=True)
    symptomps=serializers.CharField(label="Symptomps:", style={'base_template': 'textarea.html'})
    department=serializers.CharField(label='Department: ')
    #required=False; if this field is not required to be present during deserialization.
    release_date=serializers.DateField(label="Release Date:", required=False)
    assigned_doctor=serializers.StringRelatedField(label='Assigned Doctor:')
    


class doctorAppointmentSerializer(serializers.Serializer):
    #patient_name=serializers.SerializerMethodField('related_patient_name')
    #patient_age=serializers.SerializerMethodField('related_patient_age')
    id = serializers.IntegerField()
    appointment_date=serializers.DateField(label="Appointment Date:",)
    appointment_time=serializers.TimeField(label="Appointment Time:")
    

    def related_patient_name(self, obj):
        return obj.patient_history.patient.get_name
    
    def related_patient_age(self, obj):
        return obj.patient_history.patient.age

class FeedbackDrSerializer(serializers.Serializer):
    given = serializers.BooleanField()
    rating = serializers.IntegerField()
    comment = serializers.CharField(max_length=200)

class SlotTimeSerializer(serializers.Serializer):
    time = serializers.TimeField()
    isBooked = serializers.BooleanField(default=False)

    def create(self, validated_data):
        new_time_slot = Slot.objects.create(
            time = validated_data['time']
        )
        return new_time_slot

    def update(self, instance, validated_data):
        instance.time=validated_data.get('time', instance.time)
        instance.save()
        return instance
    

class SlotSerializer(serializers.Serializer):
    date = serializers.DateField()
    time = serializers.TimeField()
    #slots = SlotTimeSerializer(label='available slots:')
    doctor=serializers.IntegerField(label='Assigned Doctor:')

    """def create(self, validated_data):
        start_datetime = validated_data['time']
        appointment_date = validated_data['date']
        user_doctor = doctor.objects.get(pk=validated_data['doctor'])
        slot = Slot.objects.filter(time=start_datetime).update(isBooked=True)
        new_slot = Dates.objects.filter(date=appointment_date, doctor_id=user_doctor).update(slots=slot)
        return new_slot"""