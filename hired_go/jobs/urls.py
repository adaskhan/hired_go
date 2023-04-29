from django.urls import path
from . import views

urlpatterns = [
    # User
    path("api/user_login/", views.UserLoginAPIView.as_view(), name="user_login_api"),
    path("api/user_signup/", views.UserSignUpAPIView.as_view(), name="signup_api"),
    path("api/user_homepage/", views.UserHomepageAPIView.as_view(), name="user_homepage_api"),
    path("api/user_logout/", views.UserLogoutAPIView.as_view(), name="logout_api"),
    path("api/all_vacancies/", views.AllVacanciesAPIView.as_view(), name="all_jobs_api"),
    path("api/vacancies_detail/<int:pk>/", views.VacancyDetailAPIView.as_view(), name="job_detail_api"),
    path("api/vacancies_apply/<int:pk>/", views.job_apply_view, name="job_apply_api"),

    # Recruiter
    path("api/recruiter_signup/", views.RecruiterSignUpAPIView().as_view(), name="company_signup_api"),
    path("api/recruiter_login/", views.RecruiterLoginAPIView().as_view(), name="company_login_api"),
    path("api/recruiter_homepage/", views.RecruiterHomepageAPIView.as_view(), name="company_homepage_api"),
    path("api/add_vacancies/", views.AddVacancyAPIView.as_view(), name="add_job_api"),
    path("api/vacancies_list/", views.VacancyListAPIView.as_view(), name="job_list_api"),
    path("api/edit_vacancy/<int:pk>/", views.EditVacancyAPIView.as_view(), name="edit_job_api"),
    path("api/recruiter_logo/<int:pk>/", views.RecruiterLogoAPIView.as_view(), name="company_logo_api"),
    path("api/all_applicants/", views.all_applicants_view, name="all_applicants_api"),

    # Admin
    path("api/admin_login/", views.AdminLoginAPIView.as_view(), name="admin_login_api"),
    path("api/view_applicants/", views.ApplicantListAPIView.as_view(), name="view_applicants_api"),
    path("api/delete_applicant/<int:pk>/", views.ApplicantDeleteAPIView.as_view(), name="delete_applicant_api"),
    path("api/pending_recruiters/", views.PendingCompaniesListAPIView.as_view(), name="pending_companies_api"),
    path("api/accepted_recruiters/", views.AcceptedCompaniesListAPIView.as_view(), name="accepted_companies_api"),
    path("api/rejected_recruiters/", views.RejectedCompaniesAPIView.as_view(), name="rejected_companies_api"),
    path("api/all_recruiters/", views.AllCompaniesAPIView.as_view(), name="all_companies_api"),
    path("api/change_status/<int:pk>/", views.ChangeStatusAPIView.as_view(), name="change_status_api"),
    path("api/delete_recruiters/<int:pk>/", views.DeleteCompanyAPIView.as_view(), name="delete_company_api"),
]
