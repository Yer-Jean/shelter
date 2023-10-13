from django.db import models

from config import settings

NULLABLE = {'blank': True, 'null': True}


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name='Порода')
    description = models.TextField(**NULLABLE, verbose_name='Описание')

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = 'порода'
        verbose_name_plural = 'породы'


class Dog(models.Model):
    name = models.CharField(max_length=250, verbose_name='Кличка')
    # category = models.CharField(max_length=100, verbose_name='Порода')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='Порода')
    photo = models.ImageField(upload_to='dogs/', **NULLABLE, verbose_name='Фото')
    birth_day = models.DateField(**NULLABLE, verbose_name='Дата рождения')

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, **NULLABLE, verbose_name='владелец')
    # можно использовать get_user_model() вместо AUTH_USER_MODEL

    def __str__(self):
        return f'{self.name} ({self.category})'

    class Meta:
        verbose_name = 'собака'
        verbose_name_plural = 'собаки'

class Parent(models.Model):
    dog = models.ForeignKey(Dog, on_delete=models.CASCADE)
    name = models.CharField(max_length=250, verbose_name='Кличка')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='Порода')
    birth_day = models.DateField(**NULLABLE, verbose_name='Дата рождения')

    def __str__(self):
        return f'{self.name} ({self.category})'

    class Meta:
        verbose_name = 'предок'
        verbose_name_plural = 'предки'

