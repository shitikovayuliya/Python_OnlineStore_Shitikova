from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login


def home_view(request):
    """Главная страница — перенаправляет на каталог."""
    return render(request, 'users/home.html')


def register(request):
    """
    Регистрация нового пользователя.
    При успешной регистрации — автоматический вход и перенаправление на главную.
    """
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Автоматический вход после регистрации
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})
