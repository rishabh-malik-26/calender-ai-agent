
from google.oauth2 import service_account
from googleapiclient.discovery import build
import json
import os
import logging
from typing import Optional

# from utils import to_rfc3339
logging.basicConfig(level=logging.INFO,format= '%(asctime)s - %(levelname)s - %(message)s')


TIME_ZONE= 'Asia/Kolkata'

def create_calendar(calendar_name: str) -> str:

    SCOPES = ['https://www.googleapis.com/auth/calendar']

    google_creds_str = os.getenv("GOOGLE_CREDENTIALS_JSON")
    google_creds_dict = json.loads(google_creds_str)



    credentials = service_account.Credentials.from_service_account_file(
        google_creds_dict, scopes=SCOPES)

    service = build('calendar', 'v3', credentials=credentials)

    calendar = {
        'summary': calendar_name,
        'timeZone': TIME_ZONE  # Use your timezone
    }

    created_calendar = service.calendars().insert(body=calendar).execute()

    calendar_id = created_calendar['id']

    return calendar_id

# print(create_calendar('calender_2608'))

key = "e58bec6d9a942ce32ea9b3ad56a87fca1ef56044a8383e9c07487842c83e526c@group.calendar.google.com"

from typing import Optional
from datetime import datetime, timedelta
import json
import logging
from googleapiclient.discovery import build
from google.oauth2 import service_account

class Calendar:
    def __init__(self, calendar_id: str):
        """
        Initialize the Calendar manager.
        Args:
            calendar_id (str): The Google Calendar ID to use.
        """
        self.calendar_id = calendar_id
        self.service = self._authenticate()
        logging.info("Calendar Authenticated")
    
    def _authenticate(self):
        """
        Authenticate with Google Calendar API using service account.
        """
        SCOPES = ['https://www.googleapis.com/auth/calendar']
        # Load credentials from environment variable
        with open("service.json") as f:
            service_account_info = json.load(f)
        
        credentials = service_account.Credentials.from_service_account_info(
            service_account_info, scopes=SCOPES
        )
        return build('calendar', 'v3', credentials=credentials)
    
    def book_appointment(self, 
                        name: str, 
                        start_time: str, 
                        description: Optional[str] = None, 
                        end_time: Optional[str] = None, 
                        timezone: str = TIME_ZONE) -> str:
        """
        Book a new appointment (create event).
        Args:
            name (str): Title of the event.
            start_time (str): Start time in RFC3339 format, e.g., '2025-07-06T10:00:00+05:30'
            description (Optional[str]): Description. Defaults to "No description provided".
            end_time (Optional[str]): End time in RFC3339 format. Auto-calculated if not provided.
            timezone (str): Timezone.
        Returns:
            str: ID of the created event.
        """
        # Set default description if not provided
        if description is None:
            description = "No description provided"
        
        # Calculate end_time if not provided (1 hour after start_time)
        if end_time is None:
            try:
                # Parse the start_time and add 1 hour
                start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                end_dt = start_dt + timedelta(hours=1)
                end_time = end_dt.isoformat()
            except Exception as e:
                logging.error(f"Error calculating end_time: {e}")
                raise ValueError(f"Invalid start_time format: {start_time}")
        
        event = {
            'summary': name,
            'description': description,
            'start': {
                'dateTime': start_time,
                'timeZone': timezone
            },
            'end': {
                'dateTime': end_time,
                'timeZone': timezone
            }
        }
        
        created_event = self.service.events().insert(
            calendarId=self.calendar_id,
            body=event
        ).execute()
        
        logging.info(f"Appointment Booked: {event['summary']}")
        return created_event['id']
    

    def cancel_appointment_by_name(self, event_name: str) -> str:
        """
        Cancel the first matching appointment based on event name/title.
        """
        events_result = self.service.events().list(
            calendarId=self.calendar_id,
            q=event_name,
            singleEvents=True,
            orderBy="startTime"
        ).execute()

        events = events_result.get("items", [])
        if not events:
            return f"No appointment found with name '{event_name}'."

        event_id = events[0]["id"]
        self.service.events().delete(
            calendarId=self.calendar_id,
            eventId=event_id
        ).execute()
        return f"Cancelled event: {events[0]['summary']} on {events[0]['start']['dateTime']}"




    # def cancel_appointment(self, event_id: str):
    #     """
    #     Cancel (delete) an appointment by its event ID.
    #     """
    #     self.service.events().delete(
    #         calendarId=self.calendar_id,
    #         eventId=event_id
    #     ).execute()
    #     logging.info(f"Appointment {event_id} cancelled")
    
    def reschedule_appointment(self, 
                              event_id: str, 
                              new_start_time: str, 
                              new_end_time: Optional[str] = None, 
                              timezone: str = TIME_ZONE):
        """
        Reschedule an existing appointment by updating its start/end time.
        Args:
            event_id (str): The ID of the event to reschedule.
            new_start_time (str): New start time.
            new_end_time (Optional[str]): New end time. Auto-calculated if not provided.
            timezone (str): Timezone.
        """
        # Calculate new_end_time if not provided
        if new_end_time is None:
            try:
                start_dt = datetime.fromisoformat(new_start_time.replace('Z', '+00:00'))
                end_dt = start_dt + timedelta(hours=1)
                new_end_time = end_dt.isoformat()
            except Exception as e:
                logging.error(f"Error calculating new_end_time: {e}")
                raise ValueError(f"Invalid new_start_time format: {new_start_time}")
        
        event = self.service.events().get(
            calendarId=self.calendar_id,
            eventId=event_id
        ).execute()
        
        event['start']['dateTime'] = new_start_time
        event['end']['dateTime'] = new_end_time
        event['start']['timeZone'] = timezone
        event['end']['timeZone'] = timezone
        
        updated_event = self.service.events().update(
            calendarId=self.calendar_id,
            eventId=event_id,
            body=event
        ).execute()
        
        logging.info(f"Rescheduled appointment: {updated_event.get('htmlLink')}")
    
    def check_appointment(self, query: str) -> list:
        """
        Search appointments by summary (title or name of person).
        """
        events_result = self.service.events().list(
            calendarId=self.calendar_id,
            q=query,
            singleEvents=True,
            orderBy="startTime"
        ).execute()
        events = events_result.get("items", [])
        
        if not events:
            return f"No appointments found for '{query}'."
        
        return [
            {
                "summary": e.get("summary"),
                "start": e.get("start", {}).get("dateTime", e.get("start", {}).get("date")),
                "end": e.get("end", {}).get("dateTime", e.get("end", {}).get("date")),
                "id": e.get("id")
            }
            for e in events
        ]
    
    def reschedule_appointment_by_name(self, 
                                   name: str, 
                                   new_start_time: str, 
                                   new_end_time: Optional[str] = None, 
                                   timezone= TIME_ZONE) -> str:
        """
        Reschedule an appointment by its name (summary/title).

        Args:
            name (str): The summary/title of the event.
            new_start_time (str): New start time in RFC3339 format.
            new_end_time (Optional[str]): New end time. Auto-calculated if not provided.
            timezone (str): Timezone for the event.

        Returns:
            str: Link to the updated event.
        """

        # Calculate new_end_time if not given
        if not new_end_time:
            try:
                start_dt = datetime.fromisoformat(new_start_time.replace('Z', '+00:00'))
                end_dt = start_dt + timedelta(hours=1)
                new_end_time = end_dt.isoformat()
            except Exception as e:
                logging.error(f"Error calculating new_end_time: {e}")
                raise ValueError(f"Invalid new_start_time format: {new_start_time}")

        # Search for the event by name
        events_result = self.service.events().list(
            calendarId=self.calendar_id,
            q=name,
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        events = events_result.get('items', [])

        if not events:
            raise ValueError(f"No event found with name: {name}")

        # Pick the first match
        event = events[0]
        event_id = event['id']

        # Update time & timezone
        event['start']['dateTime'] = new_start_time
        event['end']['dateTime'] = new_end_time
        event['start']['timeZone'] = TIME_ZONE
        event['end']['timeZone'] = TIME_ZONE

        updated_event = self.service.events().update(
            calendarId=self.calendar_id,
            eventId=event_id,
            body=event
        ).execute()

        logging.info(f"Rescheduled appointment: {updated_event.get('htmlLink')}")

        return updated_event.get('htmlLink')


    def next_appointments(self, max_results):
        """
        Retrieve upcoming appointments.
        """
        events_result = self.service.events().list(
            calendarId=self.calendar_id,
            maxResults=max_results,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        events = events_result.get('items', [])
        logging.info(f"Retrieved {len(events)} appointments.")
        return events
    
    def list_all_appointments(self) -> list:
        """
        Lists all upcoming appointments.
        """
        events_result = self.service.events().list(
            calendarId=self.calendar_id,
            singleEvents=True,
            orderBy="startTime"
        ).execute()
        events = events_result.get("items", [])
        
        if not events:
            return "No upcoming appointments."
        
        return [
            {
                "summary": e.get("summary"),
                "start": e.get("start", {}).get("dateTime", e.get("start", {}).get("date")),
                "end": e.get("end", {}).get("dateTime", e.get("end", {}).get("date")),
            }
            for e in events
        ]
