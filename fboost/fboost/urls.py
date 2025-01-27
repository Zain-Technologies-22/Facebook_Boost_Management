from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from accounts.views import signup_view
from django.conf.urls.static import static


admin.site.site_header = 'FBoost Admin Portal' 
admin.site.site_title = 'FBoost'   
admin.site.index_title = 'Welcome to FBoost Admin Portal'



urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('dashboard.urls')),
    path('login/', auth_views.LoginView.as_view(template_name='auth/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path('signup/', signup_view, name='signup'), 
    path('', include('credits.urls')),
    path('accounts/', include('accounts.urls')),
    path('credits/', include('credits.urls')),
    path('campaign/', include('campaign.urls')),



]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)