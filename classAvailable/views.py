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
        event_list = syncEventsFromCal(classID)
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


#********************** Url Views ************************#


def makeRes(request):
    if request.user.is_authenticated:
        user = request.user

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
                print("others is none, selected are:")
                print(prefList)



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


def submitRes(request):
    if request.method == "POST":
        data=request.POST
        classes=data.get('classList').split("-")

        day=datetime.datetime.strptime(data.get('day'),"%B %d, %Y").date()
        try:
            stime=datetime.datetime.strptime(data.get('start'),"%I:%M %p").time()
        except:
            stime=datetime.datetime.strptime(data.get('start'),"%I %p").time()
        try:
            etime=datetime.datetime.strptime(data.get('end'),"%I:%M %p").time()
        except:
            etime = datetime.datetime.strptime(data.get('end'), "%I %p").time()
        rstart=datetime.datetime.combine(day,stime)
        rend=datetime.datetime.combine(day,etime)
        res=Reservation(description=data.get('desc'),student_total=data.get('capacity'),
                        instructor=data.get('instructor'), proctor_count=data.get('proctor'),
                        res_date_start=rstart,res_date_end=rend)
        for c in classes:
            cl=Classroom.objects.get(name=c)
            res.res_class.add(cl)
        res.save(existing=True)

        for c in res.res_class.all():
            new_id = generateEvent(c.name, str(res.description),
                                   str(res.instructor) + " - Proctor count: " + str(res.proctor_count),
                                   manualDateTimeToGoogle(str(res.res_date_start)),
                                   manualDateTimeToGoogle(str(res.res_date_end)))
            res.id_list.append(new_id)
        res.save(existing=True)
        print(res)
        print("----> ids:",res.id_list)

    print("Ajax call received by Django.")
    return HttpResponseRedirect('newres')
    #return HttpResponse(json.dumps({"hi":3}),content_type="application/json")


