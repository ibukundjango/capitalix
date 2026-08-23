from django.urls import path
from . import views

urlpatterns = [
    path('', views.card_list, name='card_list'),
    path('request/', views.card_request, name='card_request'),
    path('<int:card_id>/action/', views.card_action, name='card_action'),
]