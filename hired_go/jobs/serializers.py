from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from .backends import EmailOrUsernameAuthenticationBackend
from .models import User, Recruiter, Vacancy, JobSearcher, Application, Experience, Education, Resume


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)
    password = serializers.CharField()

    def validate(self, data):
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        if not (username or email) or not password:
            raise serializers.ValidationError('Must include "username/email" and "password"')

        user = EmailOrUsernameAuthenticationBackend().authenticate(request=None, username=username, password=password)

        if not user:
            raise serializers.ValidationError('Invalid login credentials')

        if not user.is_active:
            raise serializers.ValidationError('User is not active')

        data['user'] = user
        return data


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

        JobSearcher.objects.create(
            user=user,
            type="jobsearcher"  # or any other default values you want to set
        )

        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name')


class RecruiterSignUpSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(max_length=30)
    last_name = serializers.CharField(max_length=150)
    username = serializers.CharField()
    email = serializers.EmailField(max_length=255)
    password = serializers.CharField(max_length=128, write_only=True)
    password2 = serializers.CharField(max_length=128, write_only=True)
    phone = serializers.CharField(max_length=20)
    gender = serializers.CharField(max_length=10)
    company_name = serializers.CharField(max_length=100)

    class Meta:
        model = Recruiter
        fields = ['username', 'email', 'first_name', 'last_name', 'password', 'password2', 'phone', 'gender', 'company_name']
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
        password = validated_data.pop('password')
        password2 = validated_data.pop('password2')
        if password != password2:
            raise serializers.ValidationError({'password': 'Passwords must match.'})
        user = User.objects.create_user(
            username=validated_data['username'],
            password=password,
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
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


class RecruiterCompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Recruiter
        fields = ['user', 'company_name']


class VacancySerializer(serializers.ModelSerializer):
    company_name_id = RecruiterCompanySerializer(read_only=True)

    class Meta:
        model = Vacancy
        fields = '__all__'


class ApplicationGetSerializer(serializers.ModelSerializer):
    vacancy_title = serializers.CharField(source='vacancy.title', read_only=True)
    company_name = serializers.CharField(source='company.company_name', read_only=True)

    class Meta:
        model = Application
        fields = ('id', 'vacancy_title', 'company_name', 'application_date')


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
    username = serializers.CharField(required=True)
    password = serializers.CharField()

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            raise serializers.ValidationError('Must include "username" and "password"')

        user = EmailOrUsernameAuthenticationBackend().authenticate(request=None, username=username, password=password)

        if not user:
            raise serializers.ValidationError('Invalid login credentials')

        if not user.is_active:
            raise serializers.ValidationError('User is not active')

        if not user.is_superuser:
            raise serializers.ValidationError('User is not a superuser')

        data['user'] = user
        return data


class ExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Experience
        fields = ('company', 'position', 'period_start', 'period_end')


class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        fields = ('institution', 'degree', 'period_start', 'period_end')


class ResumeSerializer(serializers.ModelSerializer):
    experiences = ExperienceSerializer(many=True, read_only=True)
    educations = EducationSerializer(many=True, read_only=True)

    class Meta:
        model = Resume
        fields = '__all__'


class JobSearcherResumeSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = JobSearcher
        fields = ['id', 'phone', 'image', 'gender', 'full_name']

    def get_full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"



class ApplicationSerializer(serializers.ModelSerializer):
    company = serializers.StringRelatedField()
    applicant = JobSearcherResumeSerializer(read_only=True)
    resume = ResumeSerializer()

    class Meta:
        model = Application
        fields = ['id', 'company', 'vacancy', 'applicant', 'resume', 'application_date']
