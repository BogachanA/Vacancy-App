from django.contrib import admin
from classAvailable import views
from django.urls import path, re_path, include

urlpatterns = [
    path('populate/<str:classID>', views.populateClassCal, name='populate_cal'),
    path('timezone/', views.returnTZ, name='timezone_retrieve'),
    path('calendar/<str:className>',views.calendars, name='cal'),
    path('calVal/<str:className>',views.calVal, name='calVal'),

    path('newres',views.makeRes, name='new_reservation'),
    path('submitRes',views.submitRes, name='submit_reservation'),
    path('success/id=<str:rID>',views.resCreated,name='success'),
]