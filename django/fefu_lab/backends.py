from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from django.db.models import Q


class EmailBackend(ModelBackend):
    #Кастомный backend для аутентификации по email
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # Ищем пользователя по email или username
            user = User.objects.get(
                Q(email__iexact=username) |
                Q(username__iexact=username)
            )

            # Проверяем пароль
            if user.check_password(password):
                return user

        except User.DoesNotExist:
            return None

        except User.MultipleObjectsReturned:
            # Если несколько пользователей с таким email
            user = User.objects.filter(email=username).order_by('id').first()
            if user and user.check_password(password):
                return user
        return None
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None