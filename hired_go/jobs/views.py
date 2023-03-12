from datetime import date

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LogoutView, LoginView
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from django.utils.decorators import method_decorator
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, UpdateView, DeleteView

from .models import *


class IndexView(View):
    def get(self, request):
        return render(request, "index.html")


class UserLoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect("/")
        return render(request, "user_login.html")

    def post(self, request):
        if request.user.is_authenticated:
            return redirect("/")
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)

        if user is not None:
            user1 = JobSearcher.objects.get(user=user)
            if user1.type == "applicant":
                login(request, user)
                return redirect("/user_homepage")
        else:
            thank = True
            return render(request, "user_login.html", {"thank": thank})
        return render(request, "user_login.html")


class UserHomepageView(View):
    @method_decorator(login_required)
    def get(self, request):
        applicant = JobSearcher.objects.get(user=request.user)
        return render(request, "user_homepage.html", {'applicant': applicant})

    @method_decorator(login_required)
    def post(self, request):
        email = request.POST['email']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        phone = request.POST['phone']
        gender = request.POST['gender']
        applicant = JobSearcher.objects.get(user=request.user)

        applicant.user.email = email
        applicant.user.first_name = first_name
        applicant.user.last_name = last_name
        applicant.phone = phone
        applicant.gender = gender
        applicant.save()
        applicant.user.save()

        try:
            image = request.FILES['image']
            applicant.image = image
            applicant.save()
        except:
            pass
        alert = True
        return render(request, "user_homepage.html", {'alert': alert, 'applicant': applicant})


class AllJobsView(View):
    @method_decorator(login_required)
    def get(self, request):
        jobs = Vacancy.objects.all().order_by('-start_date')
        applicant = JobSearcher.objects.get(user=request.user)
        apply = Application.objects.filter(applicant=applicant)
        data = []
        for i in apply:
            data.append(i.job.id)
        return render(request, "all_jobs.html", {'jobs': jobs, 'data': data})


class JobDetailView(View):
    def get(self, request, myid):
        job = Vacancy.objects.get(id=myid)
        return render(request, "job_detail.html", {'job': job})


class JobApplyView(View):
    @login_required(login_url='/user_login')
    def get(self, request, myid):
        applicant = JobSearcher.objects.get(user=request.user)
        job = Vacancy.objects.get(id=myid)
        date_today = date.today()
        if job.end_date < date_today:
            closed = True
            return render(request, "job_apply.html", {'closed': closed})
        elif job.start_date > date_today:
            not_open = True
            return render(request, "job_apply.html", {'not_open': not_open})
        else:
            return render(request, "job_apply.html", {'job': job})

    @login_required(login_url='/user_login')
    def post(self, request, myid):
        applicant = JobSearcher.objects.get(user=request.user)
        job = Vacancy.objects.get(id=myid)
        date_today = date.today()
        if job.end_date < date_today or job.start_date > date_today:
            return redirect('job_apply', myid=myid)

        resume = request.FILES['resume']
        Application.objects.create(
            job=job, company=job.company, applicant=applicant, resume=resume, apply_date=date_today)
        alert = True
        return render(request, "job_apply.html", {'alert': alert, 'job': job})


class AllApplicantsView(View):
    @method_decorator(login_required)
    def get(self, request, myid):
        vacancy = Vacancy.objects.get(id=myid)
        applicants = vacancy.jobapplication_set.filter(status="Applied")
        return render(request, "all_applicants.html", {'applicants': applicants})


class SignUpView(View):
    def get(self, request):
        return render(request, 'signup.html')

    def post(self, request):
        username = request.POST['email']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        phone = request.POST['phone']
        gender = request.POST['gender']
        image = request.FILES['image']

        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return redirect('/signup')

        user = User.objects.create_user(first_name=first_name, last_name=last_name, username=username,
                                        password=password1)
        applicants = JobSearcher.objects.create(user=user, phone=phone, gender=gender, image=image, type="applicant")
        user.save()
        applicants.save()
        return render(request, "user_login.html")


class CompanySignUpView(View):
    def get(self, request):
        return render(request, 'company_signup.html')

    def post(self, request):
        username = request.POST['username']
        email = request.POST['email']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        phone = request.POST['phone']
        gender = request.POST['gender']
        image = request.FILES['image']
        company_name = request.POST['company_name']

        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return redirect('/signup')

        user = User.objects.create_user(first_name=first_name, last_name=last_name, email=email, username=username,
                                        password=password1)
        company = Recruiter.objects.create(user=user, phone=phone, gender=gender, image=image, company_name=company_name,
                                            type="company", status="pending")
        user.save()
        company.save()
        return render(request, "company_login.html")


class CompanyLoginView(View):
    def get(self, request):
        return render(request, 'company_login.html')

    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)

        if user is not None:
            user1 = Recruiter.objects.get(user=user)
            if user1.type == "company" and user1.status != "pending":
                login(request, user)
                return redirect("/company_homepage")
        else:
            alert = True
            return render(request, "company_login.html", {"alert": alert})


class CompanyHomepageView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect("/company_login")
        company = Recruiter.objects.get(user=request.user)
        return render(request, "company_homepage.html", {'company': company})

    def post(self, request):
        if not request.user.is_authenticated:
            return redirect("/company_login")
        company = Recruiter.objects.get(user=request.user)
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone = request.POST.get('phone')
        gender = request.POST.get('gender')

        company.user.email = email
        company.user.first_name = first_name
        company.user.last_name = last_name
        company.phone = phone
        company.gender = gender
        company.save()
        company.user.save()

        try:
            image = request.FILES['image']
            company.image = image
            company.save()
        except:
            pass
        alert = True
        return render(request, "company_homepage.html", {'alert': alert})


class AddJobView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect("/company_login")
        return render(request, "add_job.html")

    def post(self, request):
        if not request.user.is_authenticated:
            return redirect("/company_login")
        title = request.POST.get('job_title')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        salary = request.POST.get('salary')
        experience = request.POST.get('experience')
        location = request.POST.get('location')
        skills = request.POST.get('skills')
        description = request.POST.get('description')
        user = request.user
        company = Recruiter.objects.get(user=user)
        job = Vacancy.objects.create(company=company, title=title, start_date=start_date, end_date=end_date, salary=salary,
                                 image=company.image, experience=experience, location=location, skills=skills,
                                 description=description, creation_date=date.today())
        job.save()
        alert = True
        return render(request, "add_job.html", {'alert': alert})


class JobListView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect("/company_login")
        companies = Recruiter.objects.get(user=request.user)
        jobs = Vacancy.objects.filter(company=companies)
        return render(request, "job_list.html", {'jobs': jobs})


class EditJobView(View):
    def get(self, request, myid):
        if not request.user.is_authenticated:
            return redirect("/company_login")
        job = Vacancy.objects.get(id=myid)
        return render(request, "edit_job.html", {'job': job})

    def post(self, request, myid):
        if not request.user.is_authenticated:
            return redirect("/company_login")
        job = Vacancy.objects.get(id=myid)
        title = request.POST.get('job_title')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        salary = request.POST.get('salary')
        experience = request.POST.get('experience')
        location = request.POST.get('location')
        skills = request.POST.get('skills')
        description = request.POST.get('description')

        job.title = title
        job.salary = salary
        job.experience = experience
        job.location = location
        job.skills = skills
        job.description = description

        job.save()
        if start_date:
            job.start_date = start_date
            job.save()
        if end_date:
            job.end_date = end_date
            job.save()
        alert = True
        return render(request, "edit_job.html", {'job': job, 'alert': alert})


class CompanyLogoView(View):
    def get(self, request, myid):
        if not request.user.is_authenticated:
            return redirect("/company_login")
        job = Vacancy.objects.get(id=myid)
        return render(request, "company_logo.html", {'job': job})

    def post(self, request, myid):
        if not request.user.is_authenticated:
            return redirect("/company_login")
        job = Vacancy.objects.get(id=myid)
        image = request.FILES.get('logo')
        if image:
            job.image = image
            job.save()
            alert = True
            return render(request, "company_logo.html", {'job': job, 'alert': alert})
        else:
            return render(request, "company_logo.html", {'job': job})


class UserLogoutView(LogoutView):
    next_page = '/'


class AdminLoginView(LoginView):
    template_name = 'admin_login.html'

    def form_valid(self, form):
        user = form.get_user()
        if user.is_superuser:
            return super().form_valid(form)
        else:
            return render(self.request, self.template_name, {'alert': True})


class ApplicantListView(LoginRequiredMixin, ListView):
    model = JobSearcher
    template_name = 'view_applicants.html'
    context_object_name = 'applicants'


class ApplicantDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = User
    template_name = 'applicant_confirm_delete.html'
    success_url = reverse_lazy('applicant_list')

    def test_func(self):
        return self.request.user.is_superuser


class PendingCompaniesListView(LoginRequiredMixin, ListView):
    model = Recruiter
    template_name = 'pending_companies.html'
    context_object_name = 'companies'
    queryset = Recruiter.objects.filter(status='pending')


class ChangeStatusView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Recruiter
    template_name = 'change_status.html'
    fields = ['status']
    success_url = reverse_lazy('pending_companies_list')

    def test_func(self):
        return self.request.user.is_superuser


class AcceptedCompaniesListView(LoginRequiredMixin, ListView):
    model = Recruiter
    template_name = 'accepted_companies.html'
    context_object_name = 'companies'
    queryset = Recruiter.objects.filter(status='Accepted')


class RejectedCompaniesView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        companies = Recruiter.objects.filter(status="Rejected")
        return render(request, "rejected_companies.html", {'companies': companies})


class AllCompaniesView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        companies = Recruiter.objects.all()
        return render(request, "all_companies.html", {'companies': companies})


class DeleteCompanyView(LoginRequiredMixin, View):
    def get(self, request, myid, *args, **kwargs):
        company = Recruiter.objects.get(id=myid)
        company.delete()
        return redirect("all_companies")
