from django.urls import path, include

urlpatterns = [
    path('', include('production.api.urls')),
]
