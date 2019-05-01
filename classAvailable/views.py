from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404
from classAvailable.helpers import syncEventsFromCal, refineForMEF
from classAvailable.models import *
from django.utils import timezone

# Create your views here.
def populateClassCal(request, classID):
    if request.user.is_authenticated:
        try:
            c=get_object_or_404(Classroom,name=classID)
        except:
            raise Http404("There is no such calendar for "+classID)
            #return HttpResponse("Hello, population of " + classID + " is successful.")

        u=request.user
        event_list = syncEventsFromCal(classID)
        for d in event_list:
            parsed_data = d.split("*")
            start_date = parsed_data[0][:10]
            start_time = parsed_data[0][11:16]
            end_date = parsed_data[1][:10]
            end_time = parsed_data[1][11:16]
            description = parsed_data[2] #School specific filtering
            res = Reservation.objects.create(by=u,description=description,
                                       res_date_start=start_date+" "+start_time,
                                       res_date_end=end_date+" "+end_time)
            res.save()
            res.res_class.add(c)

        return HttpResponse("Hello, population of "+classID+" is successful.")
    else:
        return HttpResponse("Warning: You are not logged into the system. Cannot proceed!  Kendine gel.")


def returnTZ(request):
    return HttpResponse(request.session.get('django_timezone'))
