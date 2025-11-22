
# config.py

import pytz

# Your clinic's timezone (matches your assignment context)
TIMEZONE_NAME = "Asia/Kolkata"
LOCAL_TZ = pytz.timezone(TIMEZONE_NAME)

# Working hours (24h format)
WORKDAY_START_HOUR = 9   # 9 AM
WORKDAY_END_HOUR = 17    # 5 PM

# Appointment duration in minutes
DEFAULT_APPOINTMENT_DURATION_MIN = 30

# Google Calendar
DEFAULT_CALENDAR_ID = "primary"

# How far ahead (in days) we search for the next available slot
MAX_SEARCH_DAYS_AHEAD = 7

# Slot granularity in minutes
SLOT_STEP_MINUTES = 30


