from django.urls import path
from . import views


urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    # User
    path("user_login/", views.UserLoginView.as_view(), name="user_login"),
    path("signup/", views.SignUpView.as_view(), name="signup"),
    path("user_homepage/", views.UserHomepageView.as_view(), name="user_homepage"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("all_jobs/", views.AllJobsView.as_view(), name="all_jobs"),
    path("job_detail/<int:pk>/", views.JobDetailView.as_view(), name="job_detail"),
    path("job_apply/<int:pk>/", views.JobApplyView.as_view(), name="job_apply"),

    # Company
    path("company_signup/", views.CompanySignUpView.as_view(), name="company_signup"),
    path("company_login/", views.CompanyLoginView.as_view(), name="company_login"),
    path("company_homepage/", views.CompanyHomepageView.as_view(), name="company_homepage"),
    path("add_job/", views.AddJobView.as_view(), name="add_job"),
    path("job_list/", views.JobListView.as_view(), name="job_list"),
    path("edit_job/<int:pk>/", views.EditJobView.as_view(), name="edit_job"),
    path("company_logo/<int:pk>/", views.CompanyLogoView.as_view(), name="company_logo"),
    path("all_applicants/", views.AllApplicantsView.as_view(), name="all_applicants"),

    # admin
    path("admin_login/", views.AdminLoginView.as_view(), name="admin_login"),
    path("view_applicants/", views.ApplicantListView.as_view(), name="view_applicants"),
    path("delete_applicant/<int:pk>/", views.ApplicantDeleteView.as_view(), name="delete_applicant"),
    path("pending_companies/", views.PendingCompaniesListView.as_view(), name="pending_companies"),
    path("accepted_companies/", views.AcceptedCompaniesListView.as_view(), name="accepted_companies"),
    path("rejected_companies/", views.RejectedCompaniesView.as_view(), name="rejected_companies"),
    path("all_companies/", views.AllCompaniesView.as_view(), name="all_companies"),
    path("change_status/<int:pk>/", views.ChangeStatusView.as_view(), name="change_status"),
    path("delete_company/<int:pk>/", views.DeleteCompanyView.as_view(), name="delete_company"),
]
