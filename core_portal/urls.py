from django.urls import path
from . import views

urlpatterns = [
    path('', views.master_dashboard_view, name='master_dashboard'),
    path('api/quick-switch/', views.api_quick_switch, name='api_quick_switch'),
]
