from django.urls import path
from . import views

app_name = 'establecimientos'

urlpatterns = [
    path('restaurantes/', views.listado_restaurantes, name='listado_restaurantes'),
    path('alojamientos/', views.listado_alojamientos, name='listado_alojamientos'),
]
