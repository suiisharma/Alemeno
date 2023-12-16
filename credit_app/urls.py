from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_customer, name='register-customer'),
    path('check-eligibility/', views.check_loan_eligibility, name='check-eligibility'),
    path('create-loan/', views.create_loan, name='create_loan'),
    path('view-loan/<str:loan_id>', views.view_loan, name='view_loan'),
    path('view-loans/<str:customer_id>', views.view_loans, name='view_loans'),
]
