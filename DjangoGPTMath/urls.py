from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('user/', include('Users.urls')),
    path('test/', include('Tests.urls')),
    path('', include('Main.urls')),

]
