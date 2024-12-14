from django.urls import path
from . import views

urlpatterns = [
    path('', views.index_view, name='index'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('campaigns/', views.campaigns, name='campaigns'),
    path('credits/', views.credits, name='credits'),
    
    ]