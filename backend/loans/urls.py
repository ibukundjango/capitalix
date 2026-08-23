from django.urls import path
from . import views

urlpatterns = [
    path('', views.loan_list, name='loan_list'),
    path('apply/', views.loan_apply, name='loan_apply'),
]