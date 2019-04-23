from django.contrib import admin
from classAvailable import views
from django.urls import path, re_path, include

urlpatterns = [
    path('populate/<str:classID>', views.populateClassCal, name='populate_cal'),
]