from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """
    Кастомная модель пользователя.
    Наследует все поля AbstractUser (username, email, password, is_staff, is_active и др.).
    В будущем можно добавить дополнительные поля: avatar, phone, date_of_birth.
    """
    pass
