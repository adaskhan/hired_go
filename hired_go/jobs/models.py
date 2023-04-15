from enum import Enum

from django.db import models
from django.contrib.auth.models import User


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
    phone = models.CharField(max_length=20)
    image = models.ImageField(upload_to="", null=True)
    gender = models.CharField(max_length=10)
    type = models.CharField(max_length=15)

    def __str__(self):
        return self.user.first_name


class Recruiter(models.Model):
    user = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE
    )
    phone = models.CharField(max_length=20)
    image = models.ImageField(upload_to="")
    gender = models.CharField(max_length=10)
    type = models.CharField(max_length=15)
    status = models.CharField(max_length=20)
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
    company_name = models.ForeignKey(
        to=Recruiter,
        on_delete=models.CASCADE
    )
    salary = models.FloatField()
    company_logo = models.ImageField(upload_to="")
    description = models.TextField(max_length=400)
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
    company = models.CharField(max_length=200, default="")
    vacancy = models.ForeignKey(
        to=Vacancy,
        on_delete=models.CASCADE
    )
    applicant = models.ForeignKey(
        to=JobSearcher,
        on_delete=models.CASCADE
    )
    resume = models.ImageField(upload_to="")
    application_date = models.DateField()

    def __str__(self):
        return str(self.applicant)
