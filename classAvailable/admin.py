from django.contrib import admin
from .models import *

# Register your models here.

class ClassAdmin(admin.ModelAdmin):
    list_display = ('name','capacity','exam_capacity','type')
    ordering = ('name',)

class ResAdmin(admin.ModelAdmin):
    list_display = ('by','get_class_list','description','instructor','res_date_start','res_date_end')
    ordering = ('res_date_start','description')


admin.site.register(Classroom,ClassAdmin)
admin.site.register(Reservation,ResAdmin)
