from django.contrib import admin
from .models import *

# Register your models here.

class ClassAdmin(admin.ModelAdmin):
    list_display = ('name','capacity','exam_capacity','type')
    ordering = ('name',)


class TokenMAdmin(admin.ModelAdmin):
    list_display = ('user',)


class ResAdmin(admin.ModelAdmin):
    list_display = ('by','get_class_list','description','instructor','res_date_start','res_date_end')
    ordering = ('res_date_start','description')

"""
    def save_model(self, request, obj, form, change):
        from .helpers import generateEvent, manualDateTimeToGoogle
        tzname = request.session.get('django_timezone')

        generateEvent("", self.description, self.instructor + " - " + self.proctor,
                      manualDateTimeToGoogle(str(self.res_date_start)),
                      manualDateTimeToGoogle(str(self.res_date_end)))
"""

admin.site.register(Classroom,ClassAdmin)
admin.site.register(TokenManager,TokenMAdmin)
admin.site.register(Reservation,ResAdmin)
