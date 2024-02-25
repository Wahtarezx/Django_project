from django.contrib import admin
from django.urls import path, include
from .views import procces_get_view, user_form, handle_file_uploader

app_name = 'requestdataapp'

urlpatterns = [
    path('get/', procces_get_view, name='get_view'),
    path('bio/', user_form, name='user-form'),
    path('upload/', handle_file_uploader, name='upload')
]
