from django.urls import path
from . import views

urlpatterns = [
    path('', views.salary_hub_view, name='salary_hub'),
    path('payslip/<int:slip_id>/', views.payslip_detail_view, name='payslip_detail'),
    path('payslip/employee/<str:employee_id>/', views.employee_latest_payslip_view, name='employee_latest_payslip'),
    path('api/calculate/', views.api_calculate_salary, name='api_calculate_salary'),
]
