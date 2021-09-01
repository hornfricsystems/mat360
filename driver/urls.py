from django.urls import path
from . import  views
app_name='driver'

urlpatterns=[
    path('dashBoard/',views.index,name='index'),
]