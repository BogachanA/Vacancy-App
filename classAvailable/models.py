from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField
import datetime



def token_upload_path(instance, filename):
    return "/".join(["Pickles",str(instance.id), filename])

#TODO custom user
class TokenManager(models.Model):
    user = models.OneToOneField(get_user_model(),null=False, on_delete=models.CASCADE)
    token = models.FileField(upload_to=token_upload_path,null=True)

# Create your models here. Wassup
class Classroom(models.Model):
    name = models.CharField(max_length=15, null=False, default="001")
    type = models.CharField(max_length=50, null=False, default="Class")
    capacity = models.IntegerField(default=0)
    exam_capacity = models.IntegerField(default=0)
    sync_token = models.CharField(max_length=256, null=True, default=None)

    def __str__(self):
        return self.name


class Reservation(models.Model):
    by = models.ForeignKey(get_user_model(), null=False, default=1, on_delete=models.SET_DEFAULT)
    res_class = models.ManyToManyField(Classroom)
    description = models.TextField(max_length=350, default="")
    student_total = models.IntegerField(default=0)
    instructor = models.CharField(max_length=1024,null=True)
    proctor_count = models.IntegerField(null=True)
    res_date_start = models.DateTimeField(null=True)
    res_date_end = models.DateTimeField(null=True)
    id_list = ArrayField(models.CharField(max_length=256, null=True, default=None), null=True, default=None)

    def save(self, existing=False, *args, **kwargs):
        #do_something()
        from .helpers import generateEvent, manualDateTimeToGoogle
        super().save(*args, **kwargs) #TODO res_class is empty during initial save from admin panel
        '''
        for c in self.res_class.all():
            print("**********")
            print("**********")
            print("**********")
            print(c.name)
            if not existing:
                new_id=generateEvent(c.name, str(self.description),
                              str(self.instructor) + " - Proctor count: " + str(self.proctor_count),
                              manualDateTimeToGoogle(str(self.res_date_start)),
                              manualDateTimeToGoogle(str(self.res_date_end)))
                self.id_list.append(new_id)
        '''

    def __str__(self):
        if self.id:
            return "Reservation for {0} by ({1}) on {2}".format([c.name for c in self.res_class.all()],self.by,self.res_date_start)
        else:
            return "Reservation by ({0}) on {1}".format(self.by,self.res_date_start)

    def get_class_list(self):
        return ", ".join([c.name for c in self.res_class.all()])


