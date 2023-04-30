from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User, Recruiter, Vacancy, JobSearcher, Application


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if email and password:
            user = authenticate(email=email, password=password)
            if user:
                if user.is_active:
                    data['user'] = user
                    return data
                else:
                    raise serializers.ValidationError('User is not active')
            else:
                raise serializers.ValidationError('Unable to log in with provided credentials')
        else:
            raise serializers.ValidationError('Must include "email" and "password"')

    def create(self, validated_data):
        user = validated_data['user']
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }


class UserSignUpSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        username = validated_data.pop('username')
        user = User.objects.create_user(
            username=username,
            **validated_data
        )
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name')


class RecruiterSignUpSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')
    email = serializers.EmailField(max_length=255)
    password = serializers.CharField(max_length=128, write_only=True)
    password2 = serializers.CharField(max_length=128, write_only=True)
    phone = serializers.CharField(max_length=20)
    gender = serializers.CharField(max_length=10)
    company_name = serializers.CharField(max_length=100)

    class Meta:
        model = Recruiter
        fields = ['username', 'email', 'password', 'password2', 'phone', 'gender', 'company_name']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate(self, data):
        password = data.get('password')
        password2 = data.get('password2')

        if password != password2:
            raise serializers.ValidationError({"password": "Passwords must match."})

        return data

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        password = validated_data.pop('password')
        password2 = validated_data.pop('password2')
        if password != password2:
            raise serializers.ValidationError({'password': 'Passwords must match.'})
        user = User.objects.create_user(**user_data, password=password)
        recruiter = Recruiter.objects.create(
            user=user,
            email=validated_data.get('email'),
            phone=validated_data.get('phone'),
            gender=validated_data.get('gender'),
            company_name=validated_data.get('company_name')
        )

        return recruiter


class RecruiterLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if not email:
            raise serializers.ValidationError({"email": "This field is required."})

        if not password:
            raise serializers.ValidationError({"password": "This field is required."})

        user = authenticate(email=email, password=password)
        if user:
            if user.is_active:
                data['user'] = user
                return data
            else:
                raise serializers.ValidationError({"user": "User is not active"})
        else:
            raise serializers.ValidationError({"user": "Unable to log in with provided credentials"})


class RecruiterSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Recruiter
        fields = '__all__'


class ChangeStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recruiter
        fields = ('status',)


class VacancySerializer(serializers.ModelSerializer):
    class Meta:
        model = Vacancy
        fields = '__all__'


class AddVacancySerializer(serializers.ModelSerializer):
    class Meta:
        model = Vacancy
        fields = ('title', 'description', 'location', 'salary', 'vacancy_type', 'skills', 'company_name_id', 'experience', 'tech_stack', 'start_date', 'end_date')


class EditVacancySerializer(serializers.ModelSerializer):
    class Meta:
        model = Vacancy
        fields = ('title', 'description', 'location', 'salary', 'vacancy_type', 'tech_stack', 'company_logo', 'experience', 'skills', 'start_date', 'end_date')
        extra_kwargs = {
            'title': {'required': False},
            'description': {'required': False},
            'location': {'required': False},
            'salary': {'required': False},
            'experience': {'required': False},
            'skills': {'required': False},
            'start_date': {'required': False},
            'end_date': {'required': False},
        }


class JobSearcherSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()

    class Meta:
        model = JobSearcher
        fields = ('id', 'user', 'phone', 'image', 'gender', 'type')


class RecruiterLogoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recruiter
        fields = ('id', 'company_logo')


class CompanyLogoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vacancy
        fields = ('id', 'image')
        read_only_fields = ('id',)


class AdminLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(style={'input_type': 'password'})

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if email and password:
            user = authenticate(email=email, password=password)
            if user:
                if user.is_active and user.is_superuser:
                    data['user'] = user
                    return data
                else:
                    raise serializers.ValidationError('User is not active or not a superuser')
            else:
                raise serializers.ValidationError('Unable to log in with provided credentials')
        else:
            raise serializers.ValidationError('Must include "email" and "password"')


class ApplicationSerializer(serializers.ModelSerializer):
    company = serializers.StringRelatedField()

    class Meta:
        model = Application
        fields = ['id', 'company', 'vacancy', 'applicant', 'resume', 'application_date']
        read_only_fields = ['id', 'company', 'vacancy', 'applicant', 'application_date']
