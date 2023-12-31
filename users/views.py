import random

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
# Такой импорт делаем для того, чтоб ыне было конфликта имен у классов Views
from django.contrib.auth.views import LoginView as BaseLoginView
from django.contrib.auth.views import LogoutView as BaseLogoutView
from django.core.mail import send_mail
from django.shortcuts import redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, UpdateView

from config import settings
from users.forms import UserRegisterForm, UserForm
from users.models import User
from users.services import send_new_password


class LoginView(BaseLoginView):
    template_name = 'users/login.html'


class LogoutView(BaseLogoutView):
    pass


class RegisterView(CreateView):
    model = User
    form_class = UserRegisterForm
    success_url = reverse_lazy('users:login')
    template_name = 'users/register.html'

    def form_valid(self, form):
        self.object = form.save()
        # new_user = form.save()
        send_mail(
            subject='Поздравляем с регистрацией',
            message='Вы зарегистрировались на нашей платформе. Добро пожаловать!',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[self.object.email],
            # recipient_list = [new_user.email]
        )
        return super().form_valid(form)


class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    success_url = reverse_lazy('users:profile')
    form_class = UserForm

    # переопределяем этот метод для того, чтобы не передавать в URL номер редактируемого объекта (pk)
    # то есть редактировать будем всегда текущего пользователя, под которым зашли на платформу
    def get_object(self, queryset=None):
        return self.request.user


@login_required
def generate_new_password(request):
    new_password = ''.join([str(random.randint(0, 9)) for _ in range(12)])
    request.user.set_password(new_password)
    request.user.save()
    # отправку почты с новым паролем передали в сервисную прослойку - services.py
    send_new_password(request.user.email, new_password)
    return redirect(reverse('dogs:index'))
