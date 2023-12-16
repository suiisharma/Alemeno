
from django.contrib import admin
from django.urls import path,include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('start-worker/',include('background_task.urls')),
    path('',include('credit_app.urls')),
]
