from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseRedirect
from classAvailable.helpers import *
from classAvailable.models import *
from django.utils import timezone
from classAvailable.forms import *
import requests
import json

# Create your views here.
def populateClassCal(request, classID):
    if request.user.is_authenticated:
        try:
            c=get_object_or_404(Classroom,name=classID)
        except Exception as e:
            print(e)
            raise Http404("There is no such calendar for "+classID)
            #return HttpResponse("Hello, population of " + classID + " is successful.")

        u=request.user
        event_list = syncEventsFromCal(u,classID)
        if event_list:
            for d in event_list.keys():
                parsed_data = d.split("*")
                start_date = parsed_data[0][:10]
                start_time = parsed_data[0][11:16]
                end_date = parsed_data[1][:10]
                end_time = parsed_data[1][11:16]
                description = parsed_data[2] #School specific filtering
                idlist=event_list[d]
                res=Reservation(by=u, description=description, res_date_start=start_date+" "+start_time, res_date_end=end_date+" "+end_time, id_list=[idlist])



                Reservation.save(res, existing=True)

                res.res_class.add(c)

            return HttpResponse("Hello, population of "+classID+" is successful.")
        else:
            return HttpResponse("No changes on " + classID + ".")

    else:
        return HttpResponse("Warning: You are not logged into the system. Cannot proceed!  Kendine gel.")




#https://ipstack.com/quickstart
#https://www.programmableweb.com/news/how-to-use-ipstack-api-free-geolocation-and-determine-timezone-language-and-currency/sponsored-content/2018/08/15
#http://www.indjango.com/getting-user-timezone-in-django/
def returnTZ(request):
    print(request.META['REMOTE_ADDR'])
    freegeoip_response = requests.get('http://api.ipstack.com/'+request.META['REMOTE_ADDR']+'?access_key=3844949ee610a9033e126cde7e5568fe')
    freegeoip_response_json = freegeoip_response.json()
    print(freegeoip_response_json)
    #user_time_zone = freegeoip_response_json['time_zone']
    user_time_zone = freegeoip_response_json['location']['geoname_id']
    print(user_time_zone)
    if user_time_zone:
        timezone.activate(user_time_zone)
    print(timezone.now())
    return HttpResponse(user_time_zone)
    #return HttpResponse(request.session.get('django_timezone'))


OPTIONS = """{  timeFormat: "H:mm",
                header: {
                    left: 'prev,next today',
                    center: 'title',
                    right: 'month,agendaWeek,agendaDay',
                },
                allDaySlot: false,
                firstDay: 0,
                weekMode: 'liquid',
                slotMinutes: 15,
                defaultEventMinutes: 30,
                minTime: 8,
                maxTime: 20,
                editable: false,
                dayClick: function(date, allDay, jsEvent, view) {
                    if (allDay) {       
                        $('#calendar').fullCalendar('gotoDate', date)      
                        $('#calendar').fullCalendar('changeView', 'agendaDay')
                    }
                },
                eventClick: function(event, jsEvent, view) {
                    if (view.name == 'month') {     
                        $('#calendar').fullCalendar('gotoDate', event.start)      
                        $('#calendar').fullCalendar('changeView', 'agendaDay')
                    }
                },
            }"""


#********************** Url Views ************************#


def calendars(request,className):
    event_url='calVal/'+className
    print("-----")
    return render(request,'calendar.html',{'calendar_config_options':calendar_options(event_url,OPTIONS)})


def calVal(request,className):
    print("in calval")
    cl=Classroom.objects.get(name=className)
    events = Reservation.objects.filter(res_class__in=[cl])
    return HttpResponse(res_to_json(events),content_type='application/json')


def makeRes(request):
    if request.user.is_authenticated:
        user = request.user
    else:
        print('redirecting')
        return HttpResponseRedirect('/login/google-oauth2')

    if request.method == "POST":
        form = resForm(request.POST)
        if form.is_valid():
            print('Vuhu form valid')
            d=form.cleaned_data
            print(d['proctor'])
            prefList, otherList=resFromRequest(d)
            if otherList: #prefList is a dict
                return presentAlternatives(request,d,prefList,otherList)
            else: #prefList is a list
                classes = prefList
                rstart = datetime.datetime.combine(d['day'], d['start'])
                rend = datetime.datetime.combine(d['day'], d['end'])
                res = Reservation(description=d['desc'], student_total=d['capacity'],
                                  instructor=d['instructor'], proctor_count=d['proctor'],
                                  res_date_start=rstart, res_date_end=rend, id_list=[])
                res.save(existing=True)
                for c in classes:
                    res.res_class.add(c)
                for c in res.res_class.all():
                    new_id = generateEvent(user, c.name, str(res.description),
                                           str(res.instructor) + " - Proctor count: " + str(res.proctor_count),
                                           manualDateTimeToGoogle(str(res.res_date_start)),
                                           manualDateTimeToGoogle(str(res.res_date_end)))
                    res.id_list.append(new_id)
                res.save(existing=True)
                print(res)
                print("----> ids:", res.id_list)

                return HttpResponseRedirect('newres')



    else:
        form = resForm()

    context={'form':form}

    return render(request,'newReservation.html',context)


def presentAlternatives(request,form,prefs,others):
    context={'others':others}
    clashes=[]
    clashExists=False
    for x,y in prefs.items():
        if len(y)!=0:
            clashExists=True
        clashes.append((x,y))
    context['clist']=clashes
    context['form']=form
    context['clError']=clashExists
    context['resType']=form['type']

    #choiceForm=resNotPreferredForm()
    #choiceForm.changePrefs([(c,c.name) for c in prefs.keys()])
    #choiceForm.changeOthers([(o,o.name) for o in others])
    #context['cForm']=choiceForm
    #print(prefs,others)

    return render(request,'newResStepTwo.html',context)


def submitRes(request, form=None):
    if request.method == "POST":
        data=request.POST
        classes = data.get('classList').split("-")
        day = datetime.datetime.strptime(data.get('day'), "%B %d, %Y").date()
        try:
            stime = datetime.datetime.strptime(data.get('start'), "%I:%M %p").time()
        except:
            stime = datetime.datetime.strptime(data.get('start'), "%I %p").time()
        try:
            etime = datetime.datetime.strptime(data.get('end'), "%I:%M %p").time()
        except:
            etime = datetime.datetime.strptime(data.get('end'), "%I %p").time()
        print("*******∆∆∆∆∆∆∆∆******")
        print(stime, etime)
        rstart = datetime.datetime.combine(day, stime)
        rend = datetime.datetime.combine(day, etime)
        res = Reservation(description=data.get('desc'), student_total=data.get('capacity'),
                          instructor=data.get('instructor'), proctor_count=data.get('proctor'),
                          res_date_start=rstart, res_date_end=rend, id_list=[])
        res.save(existing=True)
        for c in classes:
            cl = Classroom.objects.get(name=c)
            res.res_class.add(cl)

        for c in res.res_class.all():
            new_id = generateEvent(request.user,c.name, str(res.description),
                                   str(res.instructor) + " - Proctor count: " + str(res.proctor_count),
                                   manualDateTimeToGoogle(str(res.res_date_start)),
                                   manualDateTimeToGoogle(str(res.res_date_end)))
            res.id_list.append(new_id)
        res.save(existing=True)
        print(res)
        print("----> ids:", res.id_list)

        print("Ajax call received by Django.")
        # return HttpResponseRedirect('newres')
        return HttpResponse(json.dumps({"new_id":res.id_list[0]}),content_type="application/json")


def resCreated(request, rID):
    context={}
    if rID:
        res=Reservation.objects.filter(id_list__contains=[rID]).first()
        context['res']=res
        classes=[x.name for x in res.res_class.all()]
        cs=""
        for c in classes: cs+=c+","
        context["cs"]=cs[:len(cs)-1]
        context["date"]=res.res_date_start.date().strftime("%d-%m-%Y")
        context["sTime"]=res.res_date_start.time().strftime("%H:%M")
        context["eTime"]=res.res_date_end.time().strftime("%H:%M")
        return render(request,'resSuccess.html',context)
    else:
        return HttpResponseRedirect('/')
