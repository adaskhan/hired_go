from datetime import date

from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveAPIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken

from rest_framework import generics, status
from rest_framework.parsers import FileUploadParser
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from django.contrib.auth import logout, authenticate
from django.core.exceptions import ValidationError

from .backends import EmailOrUsernameAuthenticationBackend
from .models import User, Recruiter, Vacancy, JobSearcher, Application, Resume, Experience, Education
from .serializers import (
    UserLoginSerializer,
    UserSignUpSerializer,
    UserSerializer,
    RecruiterSignUpSerializer,
    RecruiterSerializer,
    VacancySerializer,
    AddVacancySerializer,
    EditVacancySerializer,
    JobSearcherSerializer,
    AdminLoginSerializer,
    ChangeStatusSerializer,
    ApplicationSerializer, ResumeSerializer,
)
from hired_go.settings import EMAIL_HOST_USER


class CustomValidationFailed(Exception):
    pass


class UserLoginAPIView(APIView):
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as e:
            raise CustomValidationFailed(e.message)
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })


class UserSignUpAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSignUpSerializer
    permission_classes = (AllowAny,)

    def perform_create(self, serializer):
        user = serializer.save()
        subject = 'Welcome to our job portal'
        message = f'Dear {user.first_name},\n\n' \
                  f'Thank you for registering on our job portal. Your login credentials are as follows:\n\n' \
                  f'Username: {user.username}\n' \
                  f'Password: \n\n' \
                  f'Thank you,\n' \
                  f'The HiredGo Team'
        from_email = EMAIL_HOST_USER
        recipient_list = [user.email]
        send_mail(subject, message, from_email, recipient_list)


class UserHomepageAPIView(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = request.user
        serialized_data = UserSerializer(user).data
        return Response(serialized_data)

    def post(self, request):
        phone = request.data.get('phone')
        gender = request.data.get('gender')
        type = request.data.get('type')
        try:
            image = request.FILES['image']
        except KeyError:
            image = None

        job_searcher, created = JobSearcher.objects.get_or_create(user=request.user)

        job_searcher.phone = phone
        job_searcher.gender = gender
        job_searcher.type = type
        if image:
            job_searcher.image = image
        job_searcher.save()

        serialized_data = JobSearcherSerializer(job_searcher).data
        return Response(serialized_data)


class UserLogoutAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        user = request.user
        user.token = None
        user.save()
        return Response(status=status.HTTP_200_OK)


class AllVacanciesAPIView(generics.ListAPIView):
    queryset = Vacancy.objects.all()
    serializer_class = VacancySerializer
    permission_classes = (AllowAny,)


class VacancyDetailAPIView(generics.RetrieveAPIView):
    queryset = Vacancy.objects.all()
    serializer_class = VacancySerializer
    permission_classes = (IsAuthenticated,)


class RecruiterSignUpAPIView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = RecruiterSignUpSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()

            password = make_password(serializer.validated_data.get('password'))
            serializer.validated_data['password'] = password
            user = serializer.save()
            subject = 'Welcome to our job portal'
            message = f'Dear {user.user.first_name},\n\n' \
                      f'Thank you for registering on our job portal. Your login credentials are as follows:\n\n' \
                      f'Username: {user.username}\n' \
                      f'Password: {serializer.validated_data.get("password")}\n\n' \
                      f'Thank you,\n' \
                      f'The HiredGo Team'
            from_email = EMAIL_HOST_USER
            recipient_list = [user.email]
            send_mail(subject, message, from_email, recipient_list)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RecruiterLoginAPIView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = EmailOrUsernameAuthenticationBackend().authenticate(request=None, username=username, password=password)

        if user is not None:
            try:
                recruiter = Recruiter.objects.get(user=user)
            except Recruiter.DoesNotExist:
                return Response({"error": "Invalid login credentials"}, status=status.HTTP_401_UNAUTHORIZED)

            if recruiter.status == "pending":
                return Response({"error": "Account not approved yet"}, status=status.HTTP_401_UNAUTHORIZED)
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid login credentials"}, status=status.HTTP_401_UNAUTHORIZED)


class RecruiterHomepageAPIView(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        recruiter = Recruiter.objects.get(user=request.user)
        serialized_data = RecruiterSerializer(recruiter).data
        return Response(serialized_data)


class AddVacancyAPIView(generics.CreateAPIView):
    queryset = Vacancy.objects.all()
    serializer_class = AddVacancySerializer
    permission_classes = (IsAuthenticated,)


class VacancyListAPIView(generics.ListAPIView):
    queryset = Vacancy.objects.all()
    serializer_class = VacancySerializer
    permission_classes = (IsAuthenticated,)


class EditVacancyAPIView(generics.UpdateAPIView):
    queryset = Vacancy.objects.all()
    serializer_class = EditVacancySerializer
    permission_classes = (IsAuthenticated,)
    partial = True


class RecruiterLogoAPIView(APIView):
    def get(self, request, pk):
        recruiter = Recruiter.objects.get(pk=pk)
        serializer = RecruiterSerializer(recruiter)
        return Response(serializer.data)

    def put(self, request, pk):
        recruiter = Recruiter.objects.get(pk=pk)
        serializer = RecruiterSerializer(recruiter, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class JobApplyAPIView(APIView):
    parser_classes = [FileUploadParser]
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        applicant = JobSearcher.objects.get(user=request.user)
        vacancy = Vacancy.objects.get(id=pk)

        if vacancy.end_date < date.today():
            closed = True
            return Response({'closed': closed})
        elif vacancy.start_date > date.today():
            not_open = True
            return Response({'notopen': not_open})
        else:
            serializer = VacancySerializer(vacancy)
            return Response(serializer.data)

    def post(self, request, pk):
        applicant = JobSearcher.objects.get(user=request.user)
        vacancy = Vacancy.objects.get(id=pk)

        if not applicant.resumes.exists():
            return Response({'error': 'Please create a resume first.'}, status=status.HTTP_400_BAD_REQUEST)

        selected_resume_id = request.data.get('resume_id')
        selected_resume = applicant.resumes.filter(id=selected_resume_id).first()

        if not selected_resume:
            return Response({'error': 'Invalid resume ID.'}, status=status.HTTP_400_BAD_REQUEST)

        Application.objects.create(
            vacancy=vacancy,
            company=vacancy.company_name_id,
            applicant=applicant,
            resume=selected_resume,
            application_date=date.today()
        )

        send_mail(
            'Application received',
            f'Your application for {vacancy.title} has been received.',
            EMAIL_HOST_USER,
            [request.user.email],
            fail_silently=False,
        )

        recruiter = Recruiter.objects.get(user=vacancy.company_name_id.user)
        send_mail(
            f'New application for {vacancy.title}',
            f'A new job seeker has applied for {vacancy.title} on your job portal.',
            EMAIL_HOST_USER,
            [recruiter.user.email],
            fail_silently=False,
        )

        alert = True
        return Response({'alert': alert}, status=status.HTTP_201_CREATED)


class AllApplicantsAPIView(ListAPIView):
    serializer_class = ApplicationSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        recruiter = Recruiter.objects.get(user=self.request.user)
        return Application.objects.filter(company=recruiter)


class VacancyApplicantsAPIView(ListAPIView):
    serializer_class = ApplicationSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        recruiter = Recruiter.objects.get(user=self.request.user)
        vacancy_id = self.kwargs['pk']
        return Application.objects.filter(company=recruiter, vacancy_id=vacancy_id)


class UserLogoutView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)


class AdminLoginAPIView(generics.GenericAPIView):
    serializer_class = AdminLoginSerializer

    def post(self, request):
        serializer = AdminLoginSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as e:
            raise CustomValidationFailed(e.message)
        user = serializer.validated_data['user']
        if user.is_superuser:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_200_OK)
        raise CustomValidationFailed({"error": "User is not a superuser"})


class ApplicantListAPIView(generics.ListAPIView):
    permission_classes = [IsAdminUser]
    queryset = JobSearcher.objects.all()
    serializer_class = JobSearcherSerializer


class ApplicantDeleteAPIView(generics.DestroyAPIView):
    permission_classes = [IsAdminUser]
    queryset = JobSearcher.objects.all()
    serializer_class = JobSearcherSerializer


class PendingCompaniesListAPIView(generics.ListAPIView):
    permission_classes = [IsAdminUser]
    queryset = Recruiter.objects.filter(status='pending')
    serializer_class = RecruiterSerializer


class ChangeStatusAPIView(generics.UpdateAPIView):
    permission_classes = [IsAdminUser]
    queryset = Recruiter.objects.all()
    serializer_class = ChangeStatusSerializer
    lookup_field = 'user_id'
    lookup_url_kwarg = 'pk'

    def update(self, request, *args, **kwargs):
        recruiter = self.get_object()
        old_status = recruiter.status
        response = super().update(request, *args, **kwargs)
        new_status = response.data.get('status')

        if old_status != new_status and new_status in ["Accepted", "Rejected"]:
            subject = "Your account status has been updated"
            if new_status == "Accepted":
                message = f"Dear {recruiter.user.first_name},\n\n" \
                          f"Your recruiter account has been accepted. You can now log in and start posting jobs.\n\n" \
                          f"Thank you,\n" \
                          f"The HiredGo Team"
            else:  # Rejected
                message = f"Dear {recruiter.user.first_name},\n\n" \
                          f"Unfortunately, your recruiter account has been rejected. If you have any questions, please contact our support team.\n\n" \
                          f"Thank you,\n" \
                          f"The HiredGo Team"

            from_email = EMAIL_HOST_USER
            recipient_list = [recruiter.email]
            send_mail(subject, message, from_email, recipient_list)

        return response


class AcceptedCompaniesListAPIView(generics.ListAPIView):
    permission_classes = [IsAdminUser]
    queryset = Recruiter.objects.filter(status='Accepted')
    serializer_class = RecruiterSerializer


class RejectedCompaniesAPIView(generics.ListAPIView):
    permission_classes = [IsAdminUser]
    queryset = Recruiter.objects.filter(status='Rejected')
    serializer_class = RecruiterSerializer


class AllCompaniesAPIView(generics.ListAPIView):
    permission_classes = [IsAdminUser]
    queryset = Recruiter.objects.all()
    serializer_class = RecruiterSerializer


class DeleteCompanyAPIView(generics.DestroyAPIView):
    permission_classes = [IsAdminUser]
    queryset = Recruiter.objects.all()
    serializer_class = RecruiterSerializer


class InviteCandidateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        application = Application.objects.get(id=pk)
        recruiter = Recruiter.objects.get(user=request.user)
        applicant = application.applicant
        subject = 'Interview invitation'
        message = f'Dear {applicant.user.first_name},\n\n' \
                  f'We would like to invite you for an interview for the position of {application.vacancy.title} ' \
                  f'at {recruiter.company_name}. Please let us know your availability.\n\n' \
                  f'Thank you,\n' \
                  f'{recruiter.company_name} Recruitment Team'
        from_email = EMAIL_HOST_USER
        recipient_list = [applicant.user.email]
        send_mail(subject, message, from_email, recipient_list)
        return Response({'message': 'Invitation sent successfully'}, status=status.HTTP_200_OK)


class RefuseCandidateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        application = Application.objects.get(id=pk)
        recruiter = Recruiter.objects.get(user=request.user)
        applicant = application.applicant
        subject = 'Application status update'
        message = f'Dear {applicant.user.first_name},\n\n' \
                  f'We regret to inform you that we will not be proceeding with your application for the ' \
                  f'position of {application.vacancy.title} at {recruiter.company_name}. Thank you for your interest ' \
                  f'in our company.\n\n' \
                  f'Thank you,\n' \
                  f'{recruiter.company_name} Recruitment Team'
        from_email = EMAIL_HOST_USER
        recipient_list = [applicant.user.email]
        send_mail(subject, message, from_email, recipient_list)
        return Response({'message': 'Application status updated successfully'}, status=status.HTTP_200_OK)


class ResumeCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        applicant = JobSearcher.objects.get(user=request.user)

        title = request.data.get('title', '')
        contacts = request.data.get('contacts', '')
        summary = request.data.get('summary', '')
        skills = request.data.get('skills', '')
        languages = request.data.get('languages', '')
        experiences = request.data.get('experiences', [])
        educations = request.data.get('educations', [])

        # create the resume
        resume = Resume.objects.create(
            job_searcher=applicant,
            title=title,
            contacts=contacts,
            summary=summary,
            skills=skills,
            languages=languages,
        )

        # create experiences
        for experience_data in experiences:
            position = experience_data.get("position")
            company = experience_data.get("company")
            period_start = experience_data.get("start_date")
            period_end = experience_data.get("end_date")

            Experience.objects.create(
                resume=resume,
                company=company,
                position=position,
                period_start=period_start,
                period_end=period_end,
            )

        # create educations
        for education in educations:
            Education.objects.create(
                resume=resume,
                institution=education.get('institution', ''),
                degree=education.get('degree', ''),
                period_start=education.get('start_date', ''),
                period_end=education.get('end_date', ''),
            )

        applicant.resume = resume
        applicant.save()

        return Response({'success': 'Resume created successfully.'}, status=status.HTTP_201_CREATED)


class ChangeResumeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        applicant = JobSearcher.objects.get(user=request.user)

        try:
            resume = Resume.objects.get(id=pk, job_searcher=applicant)
        except Resume.DoesNotExist:
            return Response({'error': 'Resume not found.'}, status=status.HTTP_404_NOT_FOUND)

        applicant.resume = resume
        applicant.save()

        return Response({'success': 'Resume updated successfully.'})


class ResumeListAPIView(ListAPIView):
    serializer_class = ResumeSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Resume.objects.filter(job_searcher=self.request.user.jobsearcher)


class ResumeDetailAPIView(RetrieveAPIView):
    serializer_class = ResumeSerializer
    permission_classes = (IsAuthenticated,)
    lookup_field = 'pk'

    def get_queryset(self):
        job_searcher = JobSearcher.objects.get(user=self.request.user)
        return Resume.objects.filter(job_searcher=job_searcher)


class ApplicantResumeAPIView(RetrieveAPIView):
    serializer_class = ResumeSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        recruiter = Recruiter.objects.get(user=self.request.user)
        application = Application.objects.get(id=self.kwargs['pk'], company=recruiter)
        return Resume.objects.filter(job_searcher=application.applicant)

    def get_object(self):
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, pk=self.kwargs['resume_pk'])
        return obj
