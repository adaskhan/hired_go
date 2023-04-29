from abc import ABC
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from .models import User, Recruiter, Vacancy, JobSearcher


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()


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
        fields = ('id', 'email', 'first_name', 'last_name')


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

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        password = validated_data.pop('password')
        password2 = validated_data.pop('password2')
        if password != password2:
            raise serializers.ValidationError({'password': 'Passwords must match.'})
        user = User.objects.create_user(**user_data, password=password)
        recruiter = Recruiter.objects.create(user=user, **validated_data)
        # password2 = validated_data.pop('password2')
        # if validated_data['password'] != password2:
        #     raise serializers.ValidationError({'password': 'Passwords do not match.'})
        # username = validated_data.pop('username')
        # user = User.objects.create_user(
        #     username=username,
        #     email=validated_data['email'],
        #     password=validated_data['password']
        # )
        # recruiter = Recruiter.objects.create(
        #     user=user,
        #     phone=validated_data['phone'],
        #     gender=validated_data['gender'],
        #     company_name=validated_data['company_name'],
        #     type='recruiter',
        #     status='pending'
        # )
        return recruiter


class RecruiterLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()


class RecruiterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recruiter
        fields = ('user_id', 'email', 'company_name', 'status')


class VacancySerializer(serializers.ModelSerializer):
    class Meta:
        model = Vacancy
        fields = '__all__'


class AddVacancySerializer(serializers.ModelSerializer):
    class Meta:
        model = Vacancy
        fields = ('job_title', 'job_description', 'job_location', 'job_salary', 'job_type', 'job_category')


class EditVacancySerializer(serializers.ModelSerializer):
    class Meta:
        model = Vacancy
        fields = ('job_title', 'job_description', 'job_location', 'job_salary', 'job_type', 'job_category')


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
