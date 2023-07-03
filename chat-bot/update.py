import re
from datetime import datetime, timedelta
from gcsa.google_calendar import GoogleCalendar
from functions import *
from news import *

def update_me(text):
    # Get weather information
    get_weather("London")
    # Process the input text
    process_text(text)
    # Get news
    get_news(text)


def fetch_day_events(date):
    # Create a GoogleCalendar object with the credentials
    calendar = GoogleCalendar(credentials_path='client_secret.json')
    
    # Set the time range for events in a day
    if date != datetime.today().date():
        date = date.replace(hour=00, minute=00)
    end_date = date.replace(hour=23, minute=59)
    
    # Fetch the events for the specified time range
    events = calendar.get_events(time_min=date, time_max=end_date)
    return events

def fetch_events(date):
    # Create a GoogleCalendar object with the credentials
    calendar = GoogleCalendar(credentials_path='client_secret.json')
    
    # Fetch the events for the specified date
    events = calendar.get_events(time_min=date, time_max=date + timedelta(days=1))
    return events

def increment_date(day):
    # Get today's date and weekday
    today = datetime.today()
    current_weekday = today.weekday()
    
    # Calculate the number of days to the next specified weekday
    days_ahead = (day - current_weekday) % 7
    next_day = today + timedelta(days=days_ahead)
    next_week = next_day + timedelta(weeks=1)
    
    return next_day, next_week

def fetch_week_calendar_events(next_week):
    today = datetime.today()
    week_dates = []
    week_events = []
    
    # Set the start and end dates for the week
    if next_week == "":
        end_of_week = (today - timedelta(days=today.weekday()) + timedelta(days=6))
        start_of_week = today
        current_date = today
    else:
        start_of_week = next_week.replace(hour=00, minute=00, second=1, microsecond=0)
        end_of_week = (start_of_week + timedelta(days=6))
        current_date = start_of_week
    end_of_week = end_of_week.replace(hour=23, minute=59, second=59, microsecond=0)

    # Generate a list of dates for the week
    while current_date <= end_of_week:
        week_dates.append(current_date.date())
        current_date += timedelta(days=1)

    # Fetch the events for each day in the week
    for day in week_dates:
        day_events = [day, fetch_events(day)]
        week_events.append(day_events)
    
    return week_events


def fetch_weekend_calendar_events(weekend_date):
    week_events = []
    today = datetime.today()
    current_weekday = today.weekday()

    # Set the start and end dates for the weekend
    if weekend_date == "":
        start_of_weekend = today + timedelta(days=(5 - today.weekday()))
        end_of_weekend = start_of_weekend + timedelta(days=1)
    else:
        start_of_weekend = weekend_date.replace(hour=00, minute=00, second=1, microsecond=0)
        end_of_weekend = start_of_weekend + timedelta(days=1)

    end_of_weekend = end_of_weekend.replace(hour=23, minute=59, second=0, microsecond=0)
    
    # Fetch the events for Saturday and Sunday of the weekend
    sat = [start_of_weekend.date(), fetch_events(start_of_weekend.date())]
    week_events.append(sat)
    sun = [end_of_weekend.date(), fetch_events(end_of_weekend.date())]
    week_events.append(sun)

    return week_events

def process_text(text):
    day_match = re.search(r'\b(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b', text, re.IGNORECASE)
    day_numbers = dict(zip(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"], range(7)))
    today = datetime.today().date()
    
    if 'today' in text:
        # Fetch events for today
        events = fetch_events(today)
        speak_events(events, 'Today')
    elif 'day after tomorrow' in text:
        # Fetch events for the day after tomorrow
        day_after_tomorrow = today + timedelta(days=2)
        events = fetch_events(day_after_tomorrow)
        speak_events(events, 'Day After Tomorrow')
    elif 'tomorrow' in text:
        # Fetch events for tomorrow
        tomorrow = today + timedelta(days=1)
        events = fetch_events(tomorrow)
        speak_events(events, 'Tomorrow')
    elif 'next weekend' in text:
        # Fetch events for the next weekend
        _, next_weekend_start = increment_date(5)
        week_events = fetch_weekend_calendar_events(next_weekend_start)
        speak_events_range(week_events, 'next weekend')
    elif 'next week' in text:
        # Fetch events for the next week
        next_week, _ = increment_date(0)
        week_events = fetch_week_calendar_events(next_week)
        speak_events_range(week_events, 'next Week')
    elif 'next' in text:
        if day_match:
            # Fetch events for the next specified weekday
            day = day_match.group(0).title()
            day_number = day_numbers[day]
            _, next_week = increment_date(day_number)
            events = fetch_day_events(next_week)
            speak_events(events, "specific next day")
    elif 'weekend' in text:
        # Fetch events for the upcoming weekend
        week_events = fetch_weekend_calendar_events("")
        speak_events_range(week_events, 'next weekend')
    elif 'week' in text:
        # Fetch events for the current week
        week_events = fetch_week_calendar_events("")
        speak_events_range(week_events, 'This Week')
    elif day_match:
        # Fetch events for the next specified weekday
        day = day_match.group(0).title()
        day_number = day_numbers[day]
        next_day, _ = increment_date(day_number)
        events = fetch_day_events(next_day)
        speak_events(events, "specific day")
    else:
        play_sound("sound/repeat.mp3", 1, True)


def speak_events(events, title):
    # Display and speak the events for a given day
    if events:
        for event in events:
            date = event.start
            day_of_week = date.strftime("%A")
            
            try:
                time = date.time()
                time_str = time.strftime("%H:%M")
                
                if time_str < "12:00":
                    ampmtime = "at " + str(time_str) + " am"
                elif time_str < "23:59":
                    ampmtime = "at "+ str(time_str) + " pm"
                
                date = (event.start).date()
            except:
                ampmtime = 'all day'

            print()
            print(f"On {day_of_week} you have {event.summary} {ampmtime}")
            speak(f"On {day_of_week} you have {event.summary} {ampmtime}")
    else:
        speak("No events found.\n")


def speak_events_range(events, title):
    # Display and speak the events for a given date range
    if events:
        for date_event in events:
            event_obj = date_event[1]
            date_backup = date_event[0]
            
            for event in event_obj:
                day_of_week = (event.start).strftime("%A")
                
                try:
                    time = (event.start).time()
                    time_str = time.strftime("%H:%M")
                    
                    if time_str < "12:00":
                        ampmtime = "at " + str(time_str) + " am"
                    elif time_str < "23:59":
                        ampmtime = "at "+ str(time_str) + " pm"
                    
                    date = (event.start).date()
                except:
                    ampmtime = 'all day'
                    date = date_backup

                print()
                print(f"On {day_of_week} you have {event.summary} {ampmtime}")
                speak(f"On {day_of_week} you have {event.summary} {ampmtime}")
    else:
        speak("No events found.\n")
