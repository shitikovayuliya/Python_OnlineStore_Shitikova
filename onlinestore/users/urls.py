from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

# URL-шаблоны для модуля users (аутентификация)

urlpatterns = [
    path('', views.home_view, name='home'),                          # Главная страница
    path('register/', views.register, name='register'),              # Регистрация
    path('login/', auth_views.LoginView.as_view(
        template_name='registration/login.html'
    ), name='login'),                                               # Вход
    path('logout/', auth_views.LogoutView.as_view(
        template_name='registration/logout.html'
    ), name='logout'),                                              # Выход
]
