from django.urls import path
from . import views

urlpatterns = [
    path('ChargesCount/', views.homePage, name='generate-file-ChargesCounts'),
    path('generate-file-ChargesCounts', views.generate_file_ChargesCounts, name='generate_file_ChargesCounts'),
]
