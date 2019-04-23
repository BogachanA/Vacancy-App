from django.db import models
from django.contrib.auth import get_user_model
import datetime


# Create your models here.
class Classroom(models.Model):
    name = models.CharField(max_length=15, null=False, default="001")
    type = models.CharField(max_length=50, null=False, default="Class")
    capacity = models.IntegerField(default=0)
    exam_capacity = models.IntegerField(default=0)
    # Reservations

    def __str__(self):
        return self.name


class Reservation(models.Model):
    by = models.ForeignKey(get_user_model(), null=False, default=1, on_delete=models.SET_DEFAULT) #TODO user
    res_class = models.ManyToManyField(Classroom)
    student_total = models.IntegerField(default=0)
    instructor = models.CharField(max_length=100, null=True)
    proctor = models.CharField(max_length=100, null=True)
    res_date_start = models.DateTimeField(null=True)
    res_date_end = models.DateTimeField(null=True)

    def __str__(self):
        return "Reservation for {0} by ({1}) on {2}".format(self.get_class_list(),self.instructor,self.res_date_start)

    def get_class_list(self):
        return ", ".join([c.name for c in self.res_class.all()])


