from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.custom_login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),
    path('employees/', views.employee_list, name='employee_list'),
    path('employees/<int:user_id>/role/', views.employee_role, name='employee_role'),
    path('employees/<int:user_id>/delete/', views.employee_delete, name='employee_delete'),
]
