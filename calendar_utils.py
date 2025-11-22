

# calendar_utils.py
# DEMO MODE – no real Google Calendar access.
# This version is enough to make your project run and show a full booking flow.
# calendar_utils.py
# DEMO MODE - No Google Calendar required

import datetime
from typing import List

from config import LOCAL_TZ, DEFAULT_APPOINTMENT_DURATION_MIN, DEFAULT_CALENDAR_ID


def get_calendar_service():
    """
    Demo mode: we don't connect to real Google Calendar.
    Just return a dummy object.
    """
    return "FAKE_SERVICE"


def is_slot_available(
    service,
    start_dt: datetime.datetime,
    end_dt: datetime.datetime,
    calendar_id: str = DEFAULT_CALENDAR_ID,
) -> bool:
    """
    Demo mode: pretend all slots are always available.
    """
    return True


def create_appointment_event(
    service,
    patient_name: str,
    reason: str,
    start_dt: datetime.datetime,
    end_dt: datetime.datetime,
    calendar_id: str = DEFAULT_CALENDAR_ID,
) -> dict:
    """
    Demo mode: mimic a Google Calendar event response without
    actually creating anything online.
    """
    return {
        "summary": f"Doctor Appointment - {patient_name}",
        "htmlLink": "https://calendar.google.com/demo-mode-no-real-event",
        "start": {"dateTime": start_dt.isoformat()},
        "end": {"dateTime": end_dt.isoformat()},
        "description": f"Patient: {patient_name}\nReason: {reason or '(not specified)'}",
    }


def find_next_available_slots(
    service,
    preferred_start: datetime.datetime,
    duration_minutes: int = DEFAULT_APPOINTMENT_DURATION_MIN,
    calendar_id: str = DEFAULT_CALENDAR_ID,
    max_slots: int = 3,
) -> List[datetime.datetime]:
    """
    Demo mode: just propose a few fake future slots starting from the preferred time,
    spaced 1 hour apart.
    """
    if preferred_start.tzinfo is None:
        preferred_start = LOCAL_TZ.localize(preferred_start)

    slots: List[datetime.datetime] = []
    current = preferred_start

    for i in range(max_slots):
        slots.append(current + datetime.timedelta(hours=i))

    return slots
