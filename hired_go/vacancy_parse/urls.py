from django.urls import path

from vacancy_parse.views import vacancy_search

urlpatterns = [
    path('search/', vacancy_search, name='vacancy_search')
]
