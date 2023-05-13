from patient.models import Appointment, Feedback, Prescription, Medicine, patient
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
    specialization=serializers.ChoiceField(label='specialization:', choices=department_choice)
    address= serializers.CharField(label="Address:")
    feesperSession = serializers.CharField()
    pincode= serializers.CharField(label="Pin Code:")
    mobile=serializers.CharField(label="Mobile Number:", max_length=20)
    pic = serializers.ImageField(required=False)


    def validate_mobile(self, mobile):
        if mobile.isdigit()==False:
            raise serializers.ValidationError('Please Enter a valid mobile number!')
        return mobile
    
    def create(self, validated_data):
        try: 
            new_doctor= doctor.objects.create(
                specialization=validated_data['specialization'],
                address=validated_data['address'],
                feesperSession = validated_data['feesperSession'],
                pincode = validated_data['pincode'],
                mobile=validated_data['mobile'],
                pic=validated_data['pic'],
                user=validated_data['user']
            )
        except KeyError:
            new_doctor= doctor.objects.create(
                specialization=validated_data['specialization'],
                address=validated_data['address'],
                feesperSession = validated_data['feesperSession'],
                pincode = validated_data['pincode'],
                mobile=validated_data['mobile'],
                user=validated_data['user']
            )
        return new_doctor
    
    def update(self, instance, validated_data):
        instance.specialization=validated_data.get('specialization', instance.specialization)
        instance.address=validated_data.get('address', instance.address)
        instance.pincode=validated_data.get('pincode', instance.pincode)
        instance.feesperSession=validated_data.get('feesperSession', instance.feesperSession)
        instance.mobile=validated_data.get('mobile', instance.mobile)
        instance.save()
        return instance
    
class PatientProfileSerializer(serializers.Serializer):
    age=serializers.DecimalField(label="Age:", max_digits=4,decimal_places=1)
    address= serializers.CharField(label="Address:")
    pincode = serializers.CharField()
    mobile=serializers.CharField(label="Mobile Number:", max_length=20)
    pic = serializers.ImageField(required=False)
    email = serializers.EmailField(label="Email: ")
    patient_name = serializers.SerializerMethodField('related_patient_name')

    def related_patient_name(self, obj):
        return obj.get_name

class doctorAppointmentSerializer(serializers.Serializer):
    patient_name=serializers.SerializerMethodField('related_patient_name')
    patient_age=serializers.SerializerMethodField('related_patient_age')
    id = serializers.PrimaryKeyRelatedField(read_only=True)
    status = serializers.CharField()
    appointment_date=serializers.DateField(label="Appointment Date:",)
    appointment_time=serializers.TimeField(label="Appointment Time:")
    symptoms = serializers.CharField()
    meeting_link = serializers.CharField()
    
    def update(self, instance, validated_data):
        instance.meeting_link =validated_data.get('meeting_link', instance.meeting_link)
        instance.appointment_date =validated_data.get('appointment_date', instance.appointment_date)
        instance.appointment_time =validated_data.get('appointment_time', instance.appointment_time)
        instance.symptoms =validated_data.get('symptoms', instance.symptoms)
        instance.status = validated_data.get('status',instance.status)
        instance.save()
        return instance

    def related_patient_name(self, obj):
        return obj.patient.get_name
    
    def related_patient_age(self, obj):
        return obj.patient.age

class FeedbackDrSerializer(serializers.Serializer):
    given = serializers.BooleanField()
    rating = serializers.IntegerField()
    comment = serializers.CharField(max_length=200)

class SlotTimeSerializer(serializers.Serializer):
    time = serializers.TimeField()
    isBooked = serializers.BooleanField(default=False)
    date = serializers.SlugRelatedField(slug_field='date',queryset=Dates.objects.all())

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