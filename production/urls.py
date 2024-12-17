from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('parts/', views.part_list, name='part_list'),
    path('parts/create/', views.part_create, name='part_create'),
    path('parts/<int:pk>/delete/', views.part_delete, name='part_delete'),
    path('uavs/', views.uav_list, name='uav_list'),
    path('uavs/create/', views.uav_create, name='uav_create'),
]
