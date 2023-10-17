from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.forms import inlineformset_factory
from django.http import Http404
from django.shortcuts import render
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView

from dogs.forms import DogForm, ParentForm
from dogs.models import Category, Dog, Parent


# def index(request):
#     context = {
#         'object_list': Category.objects.all()[:3],  # вывод только 3-х объектов
#         'title': 'Питомник - Главная'
#     }
#     return render(request, 'dogs/index.html', context)

class IndexView(LoginRequiredMixin, TemplateView):
    template_name = 'dogs/index.html'
    extra_context = {
        'title': 'Питомник - Главная'
    }

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data['object_list'] = Category.objects.all()[:3]
        return context_data

# ПЕРЕОПРЕДЕЛЯЕМ FBV в CBV

# def categories(request):
#     context = {
#         'object_list': Category.objects.all(),  # вывод всех объектов
#         'title': 'Питомник - все наши породы'
#     }
#     return render(request, 'dogs/category_list.html', context)


class CategoryListView(LoginRequiredMixin, ListView):
    model = Category
    # context_data['category_pk'] = category_item.pk
    extra_context = {
        'title': 'Питомник - все наши породы',
        # 'category_pk': pk
    }

    # def get_context_data(self, *args, **kwargs):
    #     context_data = super().get_context_data(*args, **kwargs)
    #
    #     category_item = Category.objects.get(pk=self.kwargs.get('pk'))
    #     context_data['category_pk'] = category_item.pk
    #     print(category_item.pk)
    #     return context_data

# ПЕРЕОПРЕДЕЛЯЕМ FBV в CBV

# def category_dogs(request, pk):
#     category_item = Category.objects.get(pk=pk)
#     context = {
#         'object_list': Dog.objects.filter(category_id=pk),
#         'title': f'Собаки породы {category_item.name}'
#     }
#     return render(request, 'dogs/dogs.html', context)


class DogListView(LoginRequiredMixin, ListView):
    model = Dog

    def get_queryset(self):
        queryset = super().get_queryset()
        # Выбираем собак только одной породы
        queryset = queryset.filter(category_id=self.kwargs.get('pk'),)
        # Если пользователь не стафф, то ему показываются только его собаки, фильтруем еще раз
        if not self.request.user.is_staff:
            queryset = queryset.filter(owner=self.request.user)
        return queryset

    # Переопределяем экстра-контекст, так как у нас подставляются динамические данные
    def get_context_data(self, *args, **kwargs):
        context_data = super().get_context_data(*args, **kwargs)

        category_item = Category.objects.get(pk=self.kwargs.get('pk'))
        context_data['category_pk'] = category_item.pk
        context_data['title'] = f'Собаки породы {category_item.name}'

        return context_data


class DogCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Dog
    form_class = DogForm
    # fields = ('name', 'category',)
    permission_required = 'dogs.add_dog'  # Создаем разрешение для стаффа на создание собак
    success_url = reverse_lazy('dogs:categories')

    def form_valid(self, form):
        self.object = form.save()
        self.object.owner = self.request.user
        self.object.save()

        return super().form_valid(form)


class CategoryDogCreateView(LoginRequiredMixin, CreateView):
    model = Dog
    fields = ('name', 'category',)
    success_url = reverse_lazy('dogs:categories')


class DogUpdateView(LoginRequiredMixin, UpdateView):
    model = Dog
    form_class = DogForm

    def get_object(self, queryset=None):
        """Получаем объект собаки для редактирования и проверяем, что ее владелец,
         тот, который сейчас вошел в систему и тот, кто - сотрудник"""
        self.object = super().get_object(queryset)
        if self.object.owner != self.request.user and not self.request.user.is_staff:
            raise Http404

        return self.object

    # Переопределяем страницу в случае успешного обновления
    def get_success_url(self):
        return reverse('dogs:dog_update', args=[self.kwargs.get('pk')])

    def get_context_data(self, *args, **kwargs):
        context_data = super().get_context_data(*args, **kwargs)

        ParentFormset = inlineformset_factory(Dog, Parent, form=ParentForm, extra=1)
        if self.request.method == 'POST':
            formset = ParentFormset(self.request.POST, instance=self.object)
        else:
            formset = ParentFormset(instance=self.object)
        context_data['formset'] = formset

        return context_data

    def form_valid(self, form):
        context_data = self.get_context_data()
        formset = context_data['formset']
        self.object = form.save()
        if formset.is_valid():
            formset.instance = self.object
            formset.save()

        return super().form_valid(form)


class DogDeleteView(LoginRequiredMixin, DeleteView):
    model = Dog
    success_url = reverse_lazy('dogs:categories')
