from django.urls import path
from . import views

urlpatterns = [
    path('', views.transaction_history, name='transaction_history'),
    path('transfer/', views.transfer_view, name='transfer'),
    path('transfer/review/', views.transfer_review, name='transfer_review'),
    path('statements/', views.statement_form, name='statement_form'),
    path('statements/<int:account_id>/<int:year>/<int:month>/', views.statement_view, name='statement_view'),
    path('statements/<int:account_id>/<int:year>/<int:month>/download/', views.statement_download, name='statement_download'),
    path('payees/', views.payee_list, name='payee_list'),
    path('payees/add/', views.payee_add, name='payee_add'),
    path('bill-pay/', views.bill_pay, name='bill_pay'),
    path('bill-pay/history/', views.bill_payment_history, name='bill_payment_history'),
    path('receipt/<int:pk>/', views.transaction_receipt, name='transaction_receipt'),
]
