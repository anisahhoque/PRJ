from django.urls import path
from . import views

urlpatterns = [
    path('tikzconverter/', views.index, name='index'),  # Define URL pattern and associate it with a view function
    
]
