from __future__ import print_function
import xlrd, xlwt
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from classAvailable.models import Classroom, Reservation

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


##############################################################
#GOOGLE CALENDAR API CALL METHODS
##############################################
SCOPES = ['https://www.googleapis.com/auth/calendar']

def getCalendarID(service,roomCode):
    page_token = None
    while True:
      calendar_list = service.calendarList().list(pageToken=page_token).execute()
      for calendar_list_entry in calendar_list['items']:
        print (calendar_list_entry['summary'])
      page_token = calendar_list.get('nextPageToken')
      print(page_token)
      if not page_token:
        break
    for i in calendar_list['items']:
        print()
        #print(i)
        print(roomCode)
        print()
        if i['summary'] == roomCode:
            print(i['summary'])
            return i['id']

    return 'none'


def syncEventsFromCal(roomCode):
    print(str(datetime.datetime.now().date())+"T"+str(datetime.datetime.now().time().replace(microsecond=0)))
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """

    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'classAvailable/credentials.json', SCOPES)
            creds = flow.run_local_server()
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)
    print(service)



    # Call the Calendar API
    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    print('Getting the upcoming 10 events')
    iddd=getCalendarID(service,roomCode=roomCode)
    print(iddd)
    #generateEvent(iddd, "deneme", "denemehoca", '2019-05-28T09:00:00', '2019-05-28T12:00:00' )
    print(service.calendars().get(calendarId=iddd).execute())
    events_result = service.events().list(calendarId=iddd, timeMin=now,
                                        maxResults=10, singleEvents=True,
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        print('No upcoming events found.')
    eventlist=[]
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        end = event['end'].get('dateTime', event['end'].get('date'))
        print(start+"*"+end+"*"+event['summary'])
        eventlist.append(start+"*"+end+"*"+event['summary'])
    return eventlist



##############################################################
#CALENDAR NAME FILTERS FOR SCHOOLS
##############################################

def refineForMEF(e):
    e=e.split(" ")
    return e[0]+" "+e[1]