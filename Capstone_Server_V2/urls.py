from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('admin/doc/', include('django.contrib.admindocs.urls')),
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('faculty/', include('faculty.urls')),
    path('accounts/login/', auth_views.LoginView.as_view()),
]