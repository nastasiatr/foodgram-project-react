from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import ASCIIUsernameValidator
from django.db import models


class User(AbstractUser):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    username = models.CharField(
        'Имя пользователя',
        max_length=settings.USERNAME_MAX_LENGTH,
        unique=True,
        help_text=(
            'Придумайте имя пользователя. Маскимально допустимое количество символов: 150. '
            'Используйте только латинские буквы, цифры и символы @/./+/-/_'
        ),
        validators=[ASCIIUsernameValidator()],
        error_messages={
            'unique': 'Пользователь с таким именем уже существует.',
        },
    )
    email = models.EmailField(
        'Электронная почта',
        max_length=settings.EMAIL_MAX_LENGTH,
        unique=True,
        help_text='Введите, пожалуйста, адрес электронной почты',
        validators=[ASCIIUsernameValidator()],
        error_messages={
            'unique': 'Пользователь с такой почтой уже существует',
        },
    )
    first_name = models.CharField(
        'Имя', max_length=settings.FIRST_NAME_MAX_LENGTH, help_text='Введите Ваше имя'
    )
    last_name = models.CharField(
        'Фамилия', max_length=settings.LAST_NAME_MAX_LENGTH, help_text='Введите Вашу фамилию'
    )

    class Meta:
        ordering = ('email',)
        db_table = 'auth_user'
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self) -> str:
        return self.get_name()

    def get_name(self):
        return self.get_full_name() or self.get_username()


class UserRelated(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        help_text='Выберите пользователя из списка',
    )

    class Meta:
        abstract = True


class Subscription(UserRelated):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name='Автор',
        help_text='Выберите автора из списка',
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                name='unique_subscription',
                fields=['user', 'author'],
            ),
            models.CheckConstraint(
                name='prevent_self_subscription',
                check=~models.Q(user=models.F('author')),
            ),
        ]
