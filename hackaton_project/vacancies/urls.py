from django.urls import path
from . import views

urlpatterns = [
    path('', views.job_search_view, name='job_search'),
]