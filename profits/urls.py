from django.urls import path
from . import views

urlpatterns = [
    path('total/<str:broker>/', views.get_total, name='get_total'),
    path('details/<str:broker>/', views.get_details, name='get_details'),
]
