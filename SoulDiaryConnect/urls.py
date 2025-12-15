"""
URL configuration for SoulDiaryConnect project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from SoulDiaryConnectApp import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('doctor/home/', views.doctor_home, name='doctor_home'),
    path('doctor/customize/', views.customize_generation, name='customize_generation'),
    path('doctor/edit-note/<int:entry_id>/', views.edit_doctor_note, name='edit_doctor_note'),
    path('patient/home/', views.patient_home, name='patient_home'),
    path('logout/', views.logout_view, name='logout'),
]