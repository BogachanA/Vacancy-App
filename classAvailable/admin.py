from django.contrib import admin
from .models import *

# Register your models here.

class ClassAdmin(admin.ModelAdmin):
    list_display = ('name','capacity','exam_capacity')
    ordering = ('name',)

class ResAdmin(admin.ModelAdmin):
    list_display = ('by','get_class_list','instructor','res_date_start','res_date_end')
    ordering = ('res_date_start','by')


admin.site.register(Classroom,ClassAdmin)
admin.site.register(Reservation,ResAdmin)
