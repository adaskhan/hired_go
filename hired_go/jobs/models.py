from enum import Enum

from django.contrib.auth.models import AbstractUser, User
from django.db import models


class VacancyType(Enum):
    remote = "Remote"
    hybrid = "Hybrid"
    office = "Office"


class TechStack(Enum):
    PYTHON = "Python"
    JAVASCRIPT = "JavaScript"
    RUBY = "Ruby"
    JAVA = "Java"
    PHP = "PHP"
    GO = "Go"
    CPLUSPLUS = "C++"
    CSHARP = "C#"
    SWIFT = "Swift"
    KOTLIN = "Kotlin"
    TYPESCRIPT = "TypeScript"
    OTHER = "Other"


class JobSearcher(models.Model):
    user = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE
    )
    phone = models.CharField(max_length=20, null=True, blank=True)
    image = models.ImageField(upload_to="", null=True, blank=True)
    gender = models.CharField(max_length=10, null=True, blank=True)
    type = models.CharField(max_length=15)
    resume = models.ForeignKey(
        to="Resume",
        on_delete=models.CASCADE,
        related_name='job_searcher_resume',
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.user.first_name


class Resume(models.Model):
    job_searcher = models.ForeignKey(
        to=JobSearcher,
        on_delete=models.CASCADE,
        related_name='resumes',
    )
    title = models.CharField(max_length=200)
    contacts = models.CharField(max_length=200)
    summary = models.TextField(max_length=500)
    skills = models.CharField(max_length=200)
    languages = models.CharField(max_length=200)
    created_date = models.DateField(auto_now_add=True)


class Recruiter(models.Model):
    user = models.OneToOneField(
        to=User,
        on_delete=models.CASCADE,
        primary_key=True
    )
    email = models.EmailField(max_length=255, unique=True, null=True)
    phone = models.CharField(max_length=20)
    image = models.ImageField(upload_to="", null=True, blank=True)
    gender = models.CharField(max_length=10)
    type = models.CharField(max_length=15, default='recruiter')
    status = models.CharField(max_length=20, default='pending')
    company_name = models.CharField(max_length=100)

    def __str__(self):
        return self.user.username


class Vacancy(models.Model):

    VACANCY_TYPE_CHOICES = [
        (VacancyType.remote.value, 'Remote'),
        (VacancyType.hybrid.value, 'Hybrid'),
        (VacancyType.office.value, 'Office'),
    ]
    TECH_STACK_CHOICES = [
        (tech_stack.value, tech_stack.value) for tech_stack in TechStack
    ]

    title = models.CharField(max_length=200)
    vacancy_type = models.CharField(
        max_length=20,
        choices=VACANCY_TYPE_CHOICES,
        default=VacancyType.office.value,
    )
    company_name_id = models.ForeignKey(
        to=Recruiter,
        on_delete=models.CASCADE
    )
    salary = models.FloatField()
    company_logo = models.ImageField(upload_to="", null=True)
    description = models.TextField()
    experience = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    skills = models.CharField(max_length=200)
    tech_stack = models.CharField(
        max_length=20,
        choices=TECH_STACK_CHOICES,
        default=TechStack.OTHER.value,
    )
    creation_date = models.DateField(auto_now_add=True)
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return self.title


class Application(models.Model):
    company = models.ForeignKey(
        to=Recruiter,
        on_delete=models.CASCADE
    )
    vacancy = models.ForeignKey(
        to=Vacancy,
        on_delete=models.CASCADE
    )
    applicant = models.ForeignKey(
        to=JobSearcher,
        on_delete=models.CASCADE
    )
    resume = models.ForeignKey(
        to=Resume,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    application_date = models.DateField()
    application_status = models.CharField(max_length=30, default="pending")

    def __str__(self):
        return str(self.applicant)


class Experience(models.Model):
    resume = models.ForeignKey(
        to=Resume,
        on_delete=models.CASCADE,
        related_name='experiences'
    )
    company = models.CharField(max_length=200, default="")
    position = models.CharField(max_length=200)
    period_start = models.DateField()
    period_end = models.DateField()


class Education(models.Model):
    resume = models.ForeignKey(
        to=Resume,
        on_delete=models.CASCADE,
        related_name='educations'
    )
    institution = models.CharField(max_length=200)
    degree = models.CharField(max_length=200)
    period_start = models.DateField()
    period_end = models.DateField()
