months = ["january", "february", "march", "april","may", "june", "july", "august","september", "october", "november", "december"]
##############################
import datetime
import re
import calendar
from functions import create_calendar_event_easy
##############################
def extract_calendar_info(input_text):
    input_text = input_text.lower()
    event = extract_calendar_event(input_text)
    day,month,year,time = extract_calendar_date_and_time(input_text)
    create_calendar_event_easy(event, day,month,year, time)
    
def extract_calendar_event(input_text):
    match = re.search(r'called\s+(.*?)\s+on', input_text)
    match2 = re.search(r'for\s+(.*?)\s+(?:on|in)', input_text)
    match3 = re.search(r'(?:a|an)\s+(.*?)\s+(?:on|for)', input_text)
    match4 = re.search(r'(?:book|add|set|create|schedule|arrange|mark)\s+(.*?)\s+(?:for|on|to)', input_text)
    event_match = re.search(r"(?i)(?:(?:book|add|set|create|schedule|arrange|called|mark)\s+)(.*?)\s+(?:on|for)", input_text)
    check  = True
    check2 = True
    check3 = True
    check4 = True
    pattern = r"\b(?:\d{1,2}(?:st|nd|rd|th)|" + "|".join(months) + r")\b"

    # Case 1: Extract event details between "called" and "on"
    if (match):
        event = match.group(1).strip()
    # Case 2: Extract event details between "for" and "in"
    elif (match2):
        event = match2.group(1).strip()
        check = re.search(r"\b(?:on|for)\s+(.*?)(?:\s+(?:as|for|in))", event, re.IGNORECASE)
        check2 = re.search(pattern, event, re.IGNORECASE)
    if ( (check) or (check2) ) and (not match):

        # Case 3: Extract event details between ["a","an"] and "on"
        if (match3):
            
            event= match3.group(1).strip()
            check3 = re.search(r"\b(?:on|for)\s+(.*?)(?:\s+(?:as|for|in))", event, re.IGNORECASE)
            check4 = re.search(pattern, event, re.IGNORECASE)
        if (check3) or (check4):
            # Case 4: Extract event details between [book,add,set,create,schedule,arrange,mark] and ["for","on","to"]
            if match4 :
                event= match4.group(1).strip()
            else:
                # Extracting event details using the original code
                event = event_match.group(1).strip() if event_match else ""
    return event.title()
    
def extract_calendar_date_and_time(input_text):
    # Get current date, month, and year

    date_match = re.search(r"\b([0-9]{1,2})(?:st|nd|rd|th)?\s+([a-zA-Z]+)", input_text, re.IGNORECASE)
    time_match = re.search(r"\b(?:[0-9]{1,2}(?::[0-9]{2})?(?:\s*(?:am|pm))?)\b", input_text, re.IGNORECASE)
    time2_match = re.search(r"\b(?:[0-9]{1,2}(?::[0-9]{2})?(?:\s*(?:am|pm))?)\b", input_text, re.IGNORECASE)
    pattern = r"\b(?:\d{1,2}(?:st|nd|rd|th)|" + "|".join(months) + r")\b"
    check5 = re.search(pattern, input_text, re.IGNORECASE)
    current_date = datetime.datetime.now().day
    current_month = datetime.datetime.now().month
    year = datetime.datetime.now().year
    current_time_full = datetime.datetime.now().time()
    current_time = current_time_full.strftime("%H:%M")

    # Extracting time
    time = time_match.group().strip() if time_match else ""
    time2 = time2_match.group().strip() if time2_match else ""

    if time:
        time = re.sub(r"(?i)\s*pm", "", time)
        time_parts = re.split(r"\s|:", time)
        hour = int(time_parts[0])
        if len(time_parts) > 1:
            minute = int(time_parts[1])
        else:
            minute = 0
        time = "{:02d}:{:02d}".format(hour % 24, minute)
    else:
        # If time is not provided, set it as "all day"
        time = "all day"

    if time2:
        phrases = ["pm", "am", "in the morning", "in the evening", "in the afternoon","p.m.","a.m."]
        for phrase in phrases:
            if phrase in input_text.lower():
                if phrase == "pm" or phrase == "in the evening" or  phrase == "p.m.":
                    if hour < 12: hour += 12
                elif phrase == "am" or phrase == "in the morning" or  phrase == "a.m.":
                    if hour == 12: hour = 0
                elif phrase == "in the afternoon":
                    if hour < 12: hour += 12
                    if hour >= 18: time2 = "all day"
                    elif hour < 10: time2 = "all day"
        time2 = "{:02d}:{:02d}".format(hour, minute)
        time = time2
    
    # Extracting date
    if check5:
        day_str = date_match.group(1).strip() if date_match else ""
        month_str = date_match.group(2).strip() if date_match else ""
        if month_str not in months:
            month_str =  ""
    else:
        day_str = ""
        month_str = ""
    # Check if date is provided
    if day_str:
        day = int(day_str)
        # Check if day and month are provided in the format "10th December"
        if month_str and day_str:
            month = datetime.datetime.strptime(month_str, "%B").month

            # Check if date is next year
            if ((day < current_date) and (month == current_month)) or (month < current_month):
                year += 1
        else:
            # If only the day is provided, use current month
            month = current_month
            if day < current_date:
                month += 1
                if month > 12:
                    month = 1
                    year += 1
    else:
        # If date is not provided, use current date and month
        if time < current_time:
            day = current_date + 1
            month = current_month

            # Check for month and year transitions
            if day > calendar.monthrange(year, current_month)[1]:
                day = 1
                month += 1

                if month > 12:
                    month = 1
                    year += 1
        else:
            day = current_date
            month = current_month
    # Format the date as dd/mm/yyyy
    #formatted_date = datetime.datetime(year, month, day).strftime("%Y-%m-%d")

    return day,month,year,time


#     #"Create a reminder on 29th for parent-teacher meeting in my calendar.",
#     "Book a time slot for yoga class on 11th October at 3 pm in my calendar.",
#     "Can you add fluffly meeting to my calendar at 9 p.m.",
#     "Arrange brunch for 19th October at 10:30 in the morning",
#     "Add an event called Dinner with GF for the 11th at 8:30 in the morning"
# ]



