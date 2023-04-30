from datetime import date

from rest_framework.generics import ListAPIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken

from rest_framework import generics, status
from rest_framework.decorators import parser_classes
from rest_framework.parsers import FileUploadParser
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token

from django.contrib.auth import login, logout, authenticate

from .models import User, Recruiter, Vacancy, JobSearcher, Application, TechStack, VacancyType
from .serializers import (
    UserLoginSerializer,
    UserSignUpSerializer,
    UserSerializer,
    RecruiterSignUpSerializer,
    RecruiterLoginSerializer,
    RecruiterSerializer,
    VacancySerializer,
    AddVacancySerializer,
    EditVacancySerializer,
    JobSearcherSerializer,
    AdminLoginSerializer,
    ChangeStatusSerializer,
    ApplicationSerializer,
)


class UserLoginAPIView(APIView):
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        user = authenticate(request, email=email, password=password)
        if not user:
            return Response({'error': 'Invalid email or password'}, status=status.HTTP_401_UNAUTHORIZED)

        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })


class UserSignUpAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSignUpSerializer
    permission_classes = (AllowAny,)


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
    permission_classes = (IsAuthenticated,)


class VacancyDetailAPIView(generics.RetrieveAPIView):
    queryset = Vacancy.objects.all()
    serializer_class = VacancySerializer
    permission_classes = (IsAuthenticated,)


class VacancyApplyAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, pk):
        vacancy = generics.get_object_or_404(Vacancy, pk=pk)
        job_searcher = JobSearcher.objects.create(user=request.user, vacancy=vacancy)
        serialized_data = JobSearcherSerializer(job_searcher).data
        return Response(serialized_data)


class RecruiterSignUpAPIView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = RecruiterSignUpSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RecruiterLoginAPIView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        user = authenticate(email=email, password=password)

        if user is not None:
            recruiter = Recruiter.objects.get(user=user)
            if recruiter.status == "pending":
                return Response({"error": "Account not approved yet"}, status=status.HTTP_401_UNAUTHORIZED)
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid email or password"}, status=status.HTTP_401_UNAUTHORIZED)


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


class JobApplyView(APIView):
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
        print(request.FILES)

        if 'file' not in request.FILES:
            return Response({'error': 'Please upload a resume.'}, status=status.HTTP_400_BAD_REQUEST)

        resume = request.FILES['file']
        Application.objects.create(
            vacancy=vacancy,
            company=vacancy.company_name_id.company_name,
            applicant=applicant,
            resume=resume,
            application_date=date.today()
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

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            if user.is_superuser:
                refresh = RefreshToken.for_user(user)
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
