from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'parts', views.PartViewSet, basename='part')
router.register(r'uavs', views.UAVViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
