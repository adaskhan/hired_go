from django.urls import path

from .views import vacancy_search

urlpatterns = [
    path('search/', vacancy_search, name='vacancy_search')
]
