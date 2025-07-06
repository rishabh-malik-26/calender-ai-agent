from calender_code import Calendar,key
from langchain.tools import tool
from datetime import datetime, timedelta

from utils import to_rfc3339
import logging
logging.basicConfig(level=logging.INFO,format= '%(asctime)s - %(levelname)s - %(message)s')


from typing import Optional
from datetime import datetime

import re
from dateutil import parser
from datetime import datetime, timedelta

calendar = Calendar(calendar_id=key)


@tool
def book_appointment(user_input: str):
    """
    Book a calendar appointment from natural language input.
    
    Args:
        user_input: Natural language description of the appointment
        
    Examples:
        "Book an appointment titled 'Google ads meeting' on 9 July at 6pm"
        "Schedule 'Team sync' tomorrow at 2pm to 3pm"
        "Book 'Doctor visit' on 2025-07-10 from 10am to 11am"
    """
    
    # print(f"DEBUG - Received input: {user_input}")
    
    try:
        # Extract appointment name/title
        name_match = re.search(r'["\']([^"\']+)["\']', user_input)
        if name_match:
            name = name_match.group(1)
        else:
            # Fallback: extract text after "titled" or "called"
            title_match = re.search(r'(?:titled|called)\s+(.+?)(?:\s+on|\s+at|\s+from|$)', user_input, re.IGNORECASE)
            if title_match:
                name = title_match.group(1).strip()
            else:
                name = "Appointment"  # Default name
        
        print(f"DEBUG - Extracted name: {name}")
        
        # Extract date and time information
        today = datetime.now()
        
        # Try to parse various date formats
        date_patterns = [
            r'on\s+(\d{1,2}\s+\w+(?:\s+\d{4})?)', 
            r'on\s+(\d{4}-\d{2}-\d{2})',          
            r'tomorrow',                            
            r'today',                 
        ]
        
        base_date = today
        for pattern in date_patterns:
            match = re.search(pattern, user_input, re.IGNORECASE)
            if match:
                if pattern == r'tomorrow':
                    base_date = today + timedelta(days=1)
                elif pattern == r'today':
                    base_date = today
                else:
                    try:
                        date_str = match.group(1)
                        # Add current year if not specified
                        if not re.search(r'\d{4}', date_str):
                            date_str += f" {today.year}"
                        base_date = parser.parse(date_str)
                    except:
                        base_date = today
                break
        
        print(f"DEBUG - Base date: {base_date}")
        
        # Extract start time
        time_patterns = [
            r'at\s+(\d{1,2}(?::\d{2})?\s*(?:am|pm))',           # "at 6pm"
            r'from\s+(\d{1,2}(?::\d{2})?\s*(?:am|pm))',         # "from 2pm"
            r'(\d{1,2}(?::\d{2})?\s*(?:am|pm))',                # "6pm"
        ]
        
        start_time_str = None
        for pattern in time_patterns:
            match = re.search(pattern, user_input, re.IGNORECASE)
            if match:
                start_time_str = match.group(1)
                break
        
        if not start_time_str:
            return {"error": "Could not extract start time from input"}
        
        print(f"DEBUG - Start time string: {start_time_str}")
        
        # Parse start time
        try:
            start_time_parsed = parser.parse(start_time_str)
            start_datetime = base_date.replace(
                hour=start_time_parsed.hour,
                minute=start_time_parsed.minute,
                second=0,
                microsecond=0
            )
        except:
            return {"error": f"Could not parse start time: {start_time_str}"}
        
        # Extract end time (optional)
        end_patterns = [
            r'to\s+(\d{1,2}(?::\d{2})?\s*(?:am|pm))',           # "to 3pm"
            r'until\s+(\d{1,2}(?::\d{2})?\s*(?:am|pm))',        # "until 7pm"
            r'from\s+\d{1,2}(?::\d{2})?\s*(?:am|pm)\s+to\s+(\d{1,2}(?::\d{2})?\s*(?:am|pm))',  # "from 2pm to 3pm"
        ]
        
        end_datetime = None
        for pattern in end_patterns:
            match = re.search(pattern, user_input, re.IGNORECASE)
            if match:
                try:
                    end_time_str = match.group(1)
                    end_time_parsed = parser.parse(end_time_str)
                    end_datetime = base_date.replace(
                        hour=end_time_parsed.hour,
                        minute=end_time_parsed.minute,
                        second=0,
                        microsecond=0
                    )
                    break
                except:
                    continue
        
        print(f"DEBUG - Start datetime: {start_datetime}")
        print(f"DEBUG - End datetime: {end_datetime}")
        
        # Convert to RFC3339 format
        start_time_rfc = start_datetime.strftime("%Y-%m-%dT%H:%M:%S+05:30")
        end_time_rfc = None
        if end_datetime:
            end_time_rfc = end_datetime.strftime("%Y-%m-%dT%H:%M:%S+05:30")
        
        print(f"DEBUG - Start time RFC: {start_time_rfc}")
        print(f"DEBUG - End time RFC: {end_time_rfc}")
        
        # Extract description (optional)
        description = None
        desc_match = re.search(r'description[:\s]+([^,\n]+)', user_input, re.IGNORECASE)
        if desc_match:
            description = desc_match.group(1).strip()
        
        # Book the appointment
        return calendar.book_appointment(
            name=name,
            start_time=start_time_rfc,
            description=description,
            end_time=end_time_rfc
        )
        
    except Exception as e:
        return {"error": f"Failed to parse appointment request: {str(e)}"}



@tool
def cancel_appointment_by_name(event_name: str):
    """Cancels a calendar appointment by appointment name."""
    return calendar.cancel_appointment_by_name(event_name)


@tool
def reschedule_appointment_by_name(event_name: str, new_start_time: str, new_end_time: Optional[str] = None):
    """
    Reschedules an appointment by getting name of the appointment
    
    Args:
        event_name: The name/title of the event to reschedule..
        new_start_time: The new start time.
        new_end_time: The new end time. Optional - defaults to 1 hour after new_start_time.
    """
    today = datetime.now().strftime("%Y-%m-%d")
    new_start_time_rfc = to_rfc3339(new_start_time, default_date=today)
    
    new_end_time_rfc = None
    if new_end_time is not None:
        new_end_time_rfc = to_rfc3339(new_end_time, default_date=today)
    
    return calendar.reschedule_appointment_by_name(event_name, new_start_time_rfc, new_end_time_rfc)

@tool
def check_appointment(query: str):
    """Checks details of a calendar appointment."""
    return calendar.check_appointment(query)

@tool
def find_next_appointments(max_results: int):
    """Checks next few appointments"""
    return calendar.next_appointments(max_results=max_results)

@tool
def list_all_appointments():
    """List all Appointments"""
    return calendar.list_all_appointments()

