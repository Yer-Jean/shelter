from django.urls import path
from django.views.decorators.cache import cache_page

from dogs.apps import DogsConfig
from dogs.views import IndexView, CategoryListView, DogListView, DogCreateView, DogUpdateView, DogDeleteView, \
    CategoryDogCreateView

app_name = DogsConfig.name

urlpatterns = [
    path('', cache_page(60)(IndexView.as_view()), name='index'),
    path('categories/', CategoryListView.as_view(), name='categories'),
    path('dogs/<int:pk>/', DogListView.as_view(), name='category'),
    path('dogs/create/', DogCreateView.as_view(), name='dog_create'),
    # Этот URL для добавления собаки внутри категории
    path('dogs/create/<int:pk>/', CategoryDogCreateView.as_view(), name='category_dog_create'),
    path('dogs/update/<int:pk>/', DogUpdateView.as_view(), name='dog_update'),
    path('dogs/delete/<int:pk>/', DogDeleteView.as_view(), name='dog_delete'),
]
