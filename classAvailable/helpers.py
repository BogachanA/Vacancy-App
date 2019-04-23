from __future__ import print_function
import xlrd, xlwt
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

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


##############################################################
#GOOGLE CALENDAR API CALL METHODS
##############################################

#client id
#706799990508-ls1tmks87ur8p41iou5bc76muv6b43lu.apps.googleusercontent.com
#client secret
#GwMSbykzaSojhQeeounO3Egz



# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar']

def getCalendarID(service,roomCode):
    page_token = None
    while True:
      calendar_list = service.calendarList().list(pageToken=page_token).execute()
      for calendar_list_entry in calendar_list['items']:
        print (calendar_list_entry['summary'])
      page_token = calendar_list.get('nextPageToken')
      if not page_token:
        break
    for i in calendar_list['items']:
        print()
        print(i['summary'])
        print(roomCode)
        print()
        if i['summary'] == roomCode:
            print(i)
            return i['id']

    return 'none'


def main():
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
                'credentials.json', SCOPES)
            creds = flow.run_local_server()
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)

    # Call the Calendar API
    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    print('Getting the upcoming 10 events')
    iddd=getCalendarID(service,'A101')
    print(iddd)
    print(service.calendars().get(calendarId=iddd).execute())
    events_result = service.events().list(calendarId=iddd, timeMin=now,
                                        maxResults=10, singleEvents=True,
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])
    reservations = []
    if not events:
        print('No upcoming events found.')
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        end = event['end'].get('dateTime', event['end'].get('date'))
        print(start,end, event['summary'])

"""  ---Event Creation Sample---


    event = {
  'summary': 'Google I/O 2015',
  'location': '800 Howard St., San Francisco, CA 94103',
  'description': 'A chance to hear more about Google\'s developer products.',
  'start': {
    'dateTime': '2015-05-28T09:00:00-07:00',
    'timeZone': 'America/Los_Angeles',
  },
  'end': {
    'dateTime': '2015-05-28T17:00:00-07:00',
    'timeZone': 'America/Los_Angeles',
  },
  'recurrence': [
    'RRULE:FREQ=DAILY;COUNT=2'
  ],
  'attendees': [
    {'email': 'lpage@example.com'},
    {'email': 'sbrin@example.com'},
  ],
  'reminders': {
    'useDefault': False,
    'overrides': [
      {'method': 'email', 'minutes': 24 * 60},
      {'method': 'popup', 'minutes': 10},
    ],
  },
}

    event = service.events().insert(calendarId='primary', body=event).execute()
    print ('Event created: %s' % (event.get('htmlLink')))

"""

print(read_data("/Users/bogachanarslan/Downloads/Book1.xls"))

