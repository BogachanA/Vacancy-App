from __future__ import print_function
import xlrd
import pickle, pytz, itertools, copy
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from .models import *
import datetime
import VacancyApp.settings as st
from django.utils import timezone
from tzlocal import get_localzone # $ pip install tzlocal

def syncAllReservations():
    classrooms=Classroom.objects.all()
    for c in classrooms:
        syncEventsFromCal(c.name)

def read_data(loc):
    #opening the excel file
    wb = xlrd.open_workbook(loc)
    sheet = wb.sheet_by_index(0)
    #creating array for the classroom data
    classroom_data = [[0 for i in range(sheet.ncols)] for j in range(sheet.nrows-1)]
    for i in range(sheet.nrows-1):
        for j in range(sheet.ncols):
            classroom_data[i][j]=sheet.cell_value(i+1, j)
    return classroom_data

#read_data("Book1.xls")
def createClassObjects():
    class_data=read_data("classAvailable/Book1.xls")
    for data in class_data:
        new_c = Classroom.objects.create(name=data[0],type=data[3],capacity=int(data[1]),exam_capacity=int(data[2]))
        new_c.save()

def manualDateTimeToGoogle(datetimeString):
    print()
    print()
    print()
    print(str(datetimeString))
    print()
    print()
    print()
    result=datetimeString.replace(" ", "T", 1).split("+")[0]
    return result



##############################################################
#GOOGLE CALENDAR API CALL METHODS
##############################################

SCOPES = ['https://www.googleapis.com/auth/calendar',
          'https://www.googleapis.com/auth/calendar.settings.readonly', ]


def getCalendarID(service, roomCode):
    page_token = None
    while True:
        calendar_list = service.calendarList().list(pageToken=page_token).execute()
        print(page_token)
        for calendar_list_entry in calendar_list['items']:
            print("")
        print (calendar_list_entry['summary'])
        page_token = calendar_list.get('nextPageToken')
        print(page_token)
        if not page_token:
            break
    for i in calendar_list['items']:
        # print(roomCode)
        if i['summary'] == roomCode:
            print(i['summary'])
            return i['id']

    return 'none'


def syncEventsFromCal(user,roomCode):
    # (str(datetime.datetime.now().date())+"T"+str(datetime.datetime.now().time().replace(microsecond=0)))
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    try:
        tm = TokenManager.objects.get(user=user)
    except TokenManager.DoesNotExist:
        tm=None
    if not tm:
        tm = TokenManager.objects.create(user=user)
        tm.save()
    try:
        path_to_token = tm.token.path
    except Exception as e:
        print(e)
        path_to_token = None
    if path_to_token:
        with open(path_to_token, 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'classAvailable/client_secret_720492882415-bebdlfp307di9ih08tuila2elnbejga1.apps.googleusercontent.com.json',
                SCOPES)
            creds = flow.run_local_server()
        # Save the credentials for the next run
        with open(st.BASE_DIR+"/media/"+"/".join(["Pickles", user.username + ".pickle"]), 'wb') as token:
            print("reobtained pickle")
            pickle.dump(creds, token)
            tm.token.name = "/".join(["Pickles", user.username + ".pickle"])
            tm.save()

    service = build('calendar', 'v3', credentials=creds)

    # Call the Calendar API
    '''
    now = (datetime.datetime.utcnow()+relativedelta(hours=-1))
    termEnd = (now+relativedelta(months=+6)).isoformat() + 'Z'  # 'Z' indicates UTC time
    now=now.isoformat() + 'Z'  # 'Z' indicates UTC time
    # print('Getting the upcoming 10 events')
    '''
    iddd = getCalendarID(service, roomCode=roomCode)
    # print(iddd)
    CURRENT_SYNC_TOKEN = Classroom.objects.get(name=roomCode).sync_token
    events_result = service.events().list(calendarId=iddd, syncToken=CURRENT_SYNC_TOKEN).execute()

    # print(CURRENT_SYNC_TOKEN)

    NEXT_SYNC_TOKEN = events_result['nextSyncToken']

    print(service.settings().list().execute())

    # print(NEXT_SYNC_TOKEN)
    print("CURRENT_SYNC_TOKEN\t" + str(CURRENT_SYNC_TOKEN))
    print("NEXT_SYNC_TOKEN\t\t" + str(NEXT_SYNC_TOKEN))
    # Classroom.objects.get(name=iddd).next_sync_token
    """
    if not CURRENT_SYNC_TOKEN:
        print("Initial Sync")
        CURRENT_SYNC_TOKEN = NEXT_SYNC_TOKEN = service.settings().list().execute()['nextSyncToken']
    """
    '''
    print(events_result)
    events = events_result.get('items', [])
    if not events:
        print('No upcoming events found.')
    eventlist = []
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        end = event['end'].get('dateTime', event['end'].get('date'))
        print(start + "*" + end + "*" + event['summary'])
        eventlist.append(start + "*" + end + "*" + event['summary'])
    # next_sync_tok= service.settings().list().execute()['nextSyncToken']

    '''
    if CURRENT_SYNC_TOKEN != NEXT_SYNC_TOKEN:
        print("\n*****")
        print("Syncing")
        print("Current Sync Token:\t" + str(CURRENT_SYNC_TOKEN))
        print("Next Sync Token:\t" + str(NEXT_SYNC_TOKEN))
        print("*****\n")

        # generateEvent(iddd, "deneme", "denemehoca", '2019-05-28T09:00:00', '2019-05-28T12:00:00' )
        # print(service.calendars().get(calendarId=iddd).execute())
        # events_result = service.events().list(calendarId=iddd, timeMin=now,).execute()
        # print(events_result)
        events = events_result.get('items', [])

        if not events:
            print('No upcoming events found.')
        eventlist = {}
        for event in events:
            print(event)
            if event['status'] == 'cancelled':
                removeEvent(roomCode, event['id'])
            else:
                updateEvent(roomCode, event['id'])

                start = event['start'].get('dateTime', event['start'].get('date'))
                end = event['end'].get('dateTime', event['end'].get('date'))
                print(start + "*" + end + "*" + event['summary'])
                eventlist[start + "*" + end + "*" + event['summary']] = event['id']
        c = Classroom.objects.get(name=roomCode)
        c.sync_token = NEXT_SYNC_TOKEN
        c.save()
        return eventlist

        # return eventlist
    elif CURRENT_SYNC_TOKEN == NEXT_SYNC_TOKEN:
        print("\n*****")
        print("No updates!")
        print("Current Sync Token:\t" + str(CURRENT_SYNC_TOKEN))
        print("Next Sync Token:\t" + str(NEXT_SYNC_TOKEN))
        print("*****\n")


##############################################################
#GOOGLE CALENDAR API CREATE EVENT METHODS
##############################################

def getUTCoffset():
    # tz = get_localzone() # local timezone #TODO TIMEZONE NOT WORKING
    d = timezone.now()  # or some other local date
    utc_offset = d.utcoffset().total_seconds()
    # print(utc_offset)
    hour, minutes = divmod(divmod(utc_offset, 60)[0], 60)
    hour, minutes = int(hour), int(minutes)
    hour_str, min_str = "", ""
    if len(str(minutes)) == 1:
        min_str = "0" + str(minutes)
    else:
        min_str = "+" + str(minutes)
    if len(str(hour)) == 1:
        hour_str = "+0" + str(hour)
    elif len(str(hour)) == 2 and hour < 0:
        hour_str = "-0" + str(hour * -1)
    else:
        hour_str = "+" + str(hour)
    # print(hour_str+min_str)
    return hour_str + ":" + min_str


def generateEvent(user, classRoom, title, instructor, start, end):
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    try:
        tm = TokenManager.objects.get(user=user)
    except TokenManager.DoesNotExist:
        tm = None
    if not tm:
        tm=TokenManager.objects.create(user=user)
        tm.save()

    try:
        path_to_token=tm.token.path
    except Exception as e:
        print(e)
        path_to_token=None
    if path_to_token:
        with open(path_to_token, 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'classAvailable/client_secret_720492882415-bebdlfp307di9ih08tuila2elnbejga1.apps.googleusercontent.com.json', SCOPES)
            creds = flow.run_local_server()
        # Save the credentials for the next run
        with open(st.BASE_DIR+"/media/"+"/".join(["Pickles", user.username + ".pickle"]), 'wb') as token:
            print("Reobtained pickle123")
            pickle.dump(creds, token)
            tm.token.name = "/".join(["Pickles", user.username + ".pickle"])
            tm.save()

    service = build('calendar', 'v3', credentials=creds)

    settings = service.settings().list().execute()
    calenderID=getCalendarID(service,classRoom)

    # print(settings)

    event = {
        'summary': title,
        'description': instructor,
        'start': {
            'dateTime': start + "+03:00", #getUTCoffset(),
            'timeZone': 'Europe/Istanbul',
        },
        'end': {
            'dateTime': end + "+03:00", #getUTCoffset(),
            'timeZone': 'Europe/Istanbul',
        },
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'email', 'minutes': 24 * 60},
                {'method': 'popup', 'minutes': 10},
            ],
        },
    }

    # TODO calendarID should vary
    event = service.events().insert(calendarId=calenderID, body=event).execute()
    print(event)
    print('Event created: %s' % (event.get('htmlLink')))
    # print(getUTCoffset())
    return event['id']


def removeEvent(roomCode, id):
    res=Reservation.objects.filter(id_list__contains=[id]).first()
    if res:
        res.id_list.remove(id)
        resses=res.res_class.all()
        if len(resses)==1:
            res.delete()
        else:
            res.res_class.remove(Classroom.objects.get(name=roomCode))

def updateEvent(roomCode, id):
    res = Reservation.objects.filter(id_list__contains=[id]).first()

    print(res)
    if not res:
        return False
    else:
        res.id_list.remove(id)
        resses = res.res_class.all()
        if len(resses) == 1:
            res.delete()
        else:
            res.res_class.remove(Classroom.objects.get(name=roomCode))
        return True



##############################################################
#CALENDAR NAME FILTERS FOR SCHOOLS
##############################################

def refineForMEF(e):
    e=e.split(" ")
    return e[0]+" "+e[1]


##############################################################
#Available Class Search Algorithm
##############################################

def isAvailable(cl,dts,dte):
    resses=Reservation.objects.filter(res_class__name=cl.name,
                                      res_date_start__day=dts.day,
                                      res_date_start__month=dts.month,
                                      res_date_start__year=dts.year)
    clashList=[]
    for r in resses:
        rds = r.res_date_start
        rde = r.res_date_end
        '''
        print(rds)
        print(rde)
        print(dts)
        print(dte)
        print("cond 1:",(rds<dte and dte<=rde))
        print("cond 2:", (rds<=dts and dts<rde))
        '''
        if rde<dts or rds>dte:
            print("cont")
            continue
        if (rds<dte and dte<=rde) or (rds<=dts and dts<rde):
            print("a")
            clashList.append(r)
        elif dts<=rds and dte>=rde:
            print("b")
            clashList.append(r)
    return clashList


def resFromRequest(form):
    #syncAllReservations()
    totalSeats=0
    finalClasses=[]
    classClashes={}

    preferred_done=False
    dts=datetime.datetime.combine(form['day'],form['start'])  #TODO timezone info from user
    dts=pytz.timezone(settings.TIME_ZONE).localize(dts)
    dte=datetime.datetime.combine(form['day'],form['end'])
    dte = pytz.timezone(settings.TIME_ZONE).localize(dte) #TODO find which timezone to compare

    list1 = copy.deepcopy(list(form['pref_class']))

    '''
    for c in list1:
        for i in range(1,len(list1)):
            combinations=itertools.combinations(list1, i)
        # print(isAvailable(c,dts,dte))
        clashes = isAvailable(c, dts, dte)
        classClashes[c] = clashes
        if len(clashes) == 0:
            totalSeats += c.exam_capacity if form['type'] == '1' else c.capacity

        if form['proctor'] in [None,0]:
            if totalSeats>form['capacity']:
                return [k for k,v in classClashes.items() if len(v)==0], None

    #print("***",classClashes,"***")
    '''
    for c in list1:
        clashes = isAvailable(c, dts, dte)
        classClashes[c] = clashes
    dictt={}

    for i in range(len(list1)):
        combinationsList=itertools.combinations(list1,i+1)
        for combination in combinationsList:
            totalSeats=0
            for c in combination:
                if len(classClashes[c])==0:
                    totalSeats+=c.exam_capacity if form['type'] == '1' else c.capacity
                    if totalSeats > form['capacity']:
                        dictt[combination]=totalSeats
                        break
    if len(dictt.values())!=0:
        min_value=min(dictt.values())
        for k,v in dictt.items():
            if min_value==v:
                return list(k), None

    list1=copy.deepcopy(list(form['pref_class']))
    for i,v in classClashes.items():
        if len(v)!=0:
            list1.remove(i)
    print("---List 1: ",list1)
    if form['proctor'] not in [None, 0] and form['proctor']<=len(list1):
        combList=itertools.combinations(list1,form['proctor'])
        for comb in combList:
            totalSeats=0
            for c in comb:
                if len(classClashes[c])==0:
                    totalSeats+=c.exam_capacity if form['type'] == '1' else c.capacity
                    if totalSeats > form['capacity']:
                        return list(comb), None


    classes = Classroom.objects.all().exclude(pk__in=form['pref_class'])
    for c in classes:
        clashes=isAvailable(c,dts,dte)
        if len(clashes)==0:
            finalClasses.append(c)
    return classClashes, finalClasses