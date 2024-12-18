from django.urls import path
from . import views

urlpatterns = [
    path('campaigns/', views.campaigns, name='campaigns'),
    path('campaigns/create/', views.create_campaign, name='create_campaign'),
    path('campaigns/<int:campaign_id>/', views.campaign_detail, name='campaign_detail'),
    path('campaigns/<int:campaign_id>/edit/', views.edit_campaign, name='edit_campaign'),
    path('campaigns/<int:campaign_id>/', views.campaign_detail, name='campaign_detail'),
]