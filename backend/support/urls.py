from django.urls import path
from . import views

urlpatterns = [
    path('', views.ticket_list, name='ticket_list'),
    path('create/', views.ticket_create, name='ticket_create'),
    path('<int:ticket_id>/', views.ticket_detail, name='ticket_detail'),
    path('chat/send/', views.chat_send_message, name='chat_send_message'),
    path('chat/email/', views.chat_send_email, name='chat_send_email'),
]