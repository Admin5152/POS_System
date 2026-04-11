from django.urls import path
from django.contrib.auth import views as auth_views
from . import views_production

app_name = 'accounts'

urlpatterns = [
    path('login/', views_production.custom_login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views_production.register, name='register'),
    path('employees/', views_production.employee_list, name='employee_list'),
    path('employees/<int:user_id>/role/', views_production.employee_role, name='employee_role'),
    path('employees/<int:user_id>/delete/', views_production.employee_delete, name='employee_delete'),
]
