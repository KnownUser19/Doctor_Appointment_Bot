
# calendar_utils_live.py
# REAL Google Calendar integration version (not used by default in demo)

import datetime
import os
from typing import List

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

from config import (
    LOCAL_TZ,
    DEFAULT_APPOINTMENT_DURATION_MIN,
    DEFAULT_CALENDAR_ID,
    WORKDAY_START_HOUR,
    WORKDAY_END_HOUR,
    MAX_SEARCH_DAYS_AHEAD,
    SLOT_STEP_MINUTES,
)

SCOPES = ["https://www.googleapis.com/auth/calendar.events"]
TOKEN_FILE = "token.json"
CREDENTIALS_FILE = "credentials.json"


def get_calendar_service():
    creds = None

    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_FILE):
                raise FileNotFoundError(
                    f"{CREDENTIALS_FILE} not found. "
                    "Create OAuth Client ID (Desktop app), download JSON and save as credentials.json."
                )

            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE, SCOPES
            )
            # ✅ use local webserver flow (this method DOES exist)
            creds = flow.run_local_server(port=0)

        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())

    service = build("calendar", "v3", credentials=creds)
    return service



def _to_rfc3339(dt: datetime.datetime) -> str:
    if dt.tzinfo is None:
        dt = LOCAL_TZ.localize(dt)
    return dt.isoformat()


def is_slot_available(
    service,
    start_dt: datetime.datetime,
    end_dt: datetime.datetime,
    calendar_id: str = DEFAULT_CALENDAR_ID,
) -> bool:
    time_min = _to_rfc3339(start_dt)
    time_max = _to_rfc3339(end_dt)

    events_result = (
        service.events()
        .list(
            calendarId=calendar_id,
            timeMin=time_min,
            timeMax=time_max,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )

    items = events_result.get("items", [])
    return len(items) == 0


def create_appointment_event(
    service,
    patient_name: str,
    reason: str,
    start_dt: datetime.datetime,
    end_dt: datetime.datetime,
    calendar_id: str = DEFAULT_CALENDAR_ID,
) -> dict:
    start_rfc3339 = _to_rfc3339(start_dt)
    end_rfc3339 = _to_rfc3339(end_dt)

    description_lines = [f"Patient: {patient_name}"]
    if reason:
        description_lines.append(f"Reason: {reason}")
    description = "\n".join(description_lines)

    event = {
        "summary": f"Doctor Appointment - {patient_name}",
        "description": description,
        "start": {
            "dateTime": start_rfc3339,
            "timeZone": start_dt.tzinfo.zone
            if start_dt.tzinfo is not None
            else LOCAL_TZ.zone,
        },
        "end": {
            "dateTime": end_rfc3339,
            "timeZone": end_dt.tzinfo.zone
            if end_dt.tzinfo is not None
            else LOCAL_TZ.zone,
        },
    }

    created_event = (
        service.events()
        .insert(calendarId=calendar_id, body=event)
        .execute()
    )
    return created_event


def _within_working_hours(dt: datetime.datetime) -> bool:
    hour = dt.hour
    return WORKDAY_START_HOUR <= hour < WORKDAY_END_HOUR


def find_next_available_slots(
    service,
    preferred_start: datetime.datetime,
    duration_minutes: int = DEFAULT_APPOINTMENT_DURATION_MIN,
    calendar_id: str = DEFAULT_CALENDAR_ID,
    max_slots: int = 3,
) -> List[datetime.datetime]:
    if preferred_start.tzinfo is None:
        preferred_start = LOCAL_TZ.localize(preferred_start)

    slot_step = datetime.timedelta(minutes=SLOT_STEP_MINUTES)
    duration = datetime.timedelta(minutes=duration_minutes)

    current = preferred_start
    if not _within_working_hours(current):
        current = current.replace(
            hour=WORKDAY_START_HOUR, minute=0, second=0, microsecond=0
        )
        if not _within_working_hours(current):
            current = current + datetime.timedelta(days=1)
            current = current.replace(
                hour=WORKDAY_START_HOUR,
                minute=0,
                second=0,
                microsecond=0,
            )

    results: List[datetime.datetime] = []
    last_allowed_date = preferred_start.date() + datetime.timedelta(
        days=MAX_SEARCH_DAYS_AHEAD
    )

    while len(results) < max_slots and current.date() <= last_allowed_date:
        if not _within_working_hours(current):
            current = current + datetime.timedelta(days=1)
            current = current.replace(
                hour=WORKDAY_START_HOUR,
                minute=0,
                second=0,
                microsecond=0,
            )
            continue

        end = current + duration

        if is_slot_available(service, current, end, calendar_id=calendar_id):
            results.append(current)

        current = current + slot_step

        if not _within_working_hours(current):
            current = current + datetime.timedelta(days=1)
            current = current.replace(
                hour=WORKDAY_START_HOUR,
                minute=0,
                second=0,
                microsecond=0,
            )

    return results
