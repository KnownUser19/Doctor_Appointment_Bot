
# dialog_manager.py

import datetime
from dataclasses import dataclass
from typing import Optional

from config import (
    LOCAL_TZ,
    DEFAULT_APPOINTMENT_DURATION_MIN,
    DEFAULT_CALENDAR_ID,
)
from calendar_utils_live import (
    is_slot_available,
    create_appointment_event,
    find_next_available_slots,
)


@dataclass
class AppointmentRequest:
    patient_name: str
    reason: str
    start_dt: datetime.datetime
    end_dt: datetime.datetime
    calendar_id: str = DEFAULT_CALENDAR_ID


def _parse_date_input(date_str: str) -> Optional[datetime.date]:
    """
    Parses a date string in YYYY-MM-DD format.
    Returns a date or None on failure.
    """
    try:
        return datetime.datetime.strptime(date_str.strip(), "%Y-%m-%d").date()
    except ValueError:
        return None


def _parse_time_input(time_str: str) -> Optional[datetime.time]:
    """
    Parses a time string in HH:MM (24-hour) format.
    Returns a time or None on failure.
    """
    try:
        return datetime.datetime.strptime(time_str.strip(), "%H:%M").time()
    except ValueError:
        return None


def _input_non_empty(prompt: str) -> str:
    """
    Get a non-empty line input from the user.
    """
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("Please enter something (it cannot be empty).")


def collect_appointment_details() -> AppointmentRequest:
    """
    Conversationally collect appointment details from the user.
    Returns an AppointmentRequest object.
    """
    print("\n--- Doctor Appointment Booking ---")

    # Name
    patient_name = _input_non_empty("Your full name: ")

    # Reason (can be empty)
    reason = input("Reason for visit (optional, press Enter to skip): ").strip()

    # Preferred date
    while True:
        date_str = input("Preferred appointment date (YYYY-MM-DD): ").strip()
        preferred_date = _parse_date_input(date_str)
        if preferred_date is None:
            print("❌ Invalid date format. Please use YYYY-MM-DD (e.g. 2025-11-25).")
            continue
        if preferred_date < datetime.date.today():
            print("❌ That date is in the past. Please choose a future date.")
            continue
        break

    # Preferred time
    while True:
        time_str = input("Preferred time (24h, HH:MM, e.g. 14:30): ").strip()
        preferred_time = _parse_time_input(time_str)
        if preferred_time is None:
            print("❌ Invalid time format. Please use HH:MM in 24-hour format.")
            continue
        break

    # Combine date & time in clinic timezone
    start_dt = datetime.datetime(
        year=preferred_date.year,
        month=preferred_date.month,
        day=preferred_date.day,
        hour=preferred_time.hour,
        minute=preferred_time.minute,
    )
    start_dt = LOCAL_TZ.localize(start_dt)

    duration = datetime.timedelta(minutes=DEFAULT_APPOINTMENT_DURATION_MIN)
    end_dt = start_dt + duration

    return AppointmentRequest(
        patient_name=patient_name,
        reason=reason,
        start_dt=start_dt,
        end_dt=end_dt,
    )


def _confirm(prompt: str) -> bool:
    """
    Simple yes/no confirmation helper.
    """
    while True:
        ans = input(f"{prompt} (y/n): ").strip().lower()
        if ans in ("y", "yes"):
            return True
        if ans in ("n", "no"):
            return False
        print("Please answer with 'y' or 'n'.")


def run_conversation(service):
    """
    Orchestrates a single booking conversation.
    """
    print("Hello! I’m your AI receptionist. I’ll help you book a doctor appointment.")

    # Step 1: Collect details
    appt_request = collect_appointment_details()

    # Step 2: Check if requested slot is available
    print("\nChecking availability for your requested time...")
    available = is_slot_available(
        service, appt_request.start_dt, appt_request.end_dt, appt_request.calendar_id
    )

    if available:
        # Offer this slot
        start_str = appt_request.start_dt.strftime("%Y-%m-%d %H:%M")
        end_str = appt_request.end_dt.strftime("%H:%M")
        print(f"✅ Great news! {start_str} - {end_str} is available.")
        if _confirm("Do you want to book this appointment?"):
            _finalize_booking(service, appt_request)
            return
        else:
            print("Okay, let’s look for another time.")
    else:
        print("⚠️ That time is not available, there is a scheduling conflict.")

    # Step 3: Suggest next available slots
    print("Searching for the next available slots...")
    suggestions = find_next_available_slots(
        service,
        preferred_start=appt_request.start_dt,
        duration_minutes=DEFAULT_APPOINTMENT_DURATION_MIN,
        calendar_id=appt_request.calendar_id,
        max_slots=3,
    )

    if not suggestions:
        print(
            "Sorry, I couldn’t find any available slots in the next few days. "
            "Please try another date."
        )
        return

    print("\nHere are the next available slots:")
    for idx, slot in enumerate(suggestions, start=1):
        end = slot + datetime.timedelta(minutes=DEFAULT_APPOINTMENT_DURATION_MIN)
        print(
            f"{idx}. {slot.strftime('%Y-%m-%d %H:%M')} - {end.strftime('%H:%M')} "
            f"({slot.tzinfo})"
        )

    print("0. Cancel")

    # Ask user to choose a slot
    chosen_slot = None
    while True:
        choice = input("Choose a slot by number (0 to cancel): ").strip()
        if not choice.isdigit():
            print("Please enter a number.")
            continue
        choice_num = int(choice)
        if choice_num == 0:
            print("Okay, cancelling the booking.")
            return
        if 1 <= choice_num <= len(suggestions):
            chosen_slot = suggestions[choice_num - 1]
            break
        else:
            print("Please choose a valid number from the list.")

    # Update appointment request with chosen slot
    appt_request.start_dt = chosen_slot
    appt_request.end_dt = chosen_slot + datetime.timedelta(
        minutes=DEFAULT_APPOINTMENT_DURATION_MIN
    )

    # Step 4: Final confirmation
    _finalize_booking(service, appt_request)


def _finalize_booking(service, appt_request: AppointmentRequest):
    """
    Confirm details with the user and create the event.
    """
    print("\nPlease review your appointment details:")
    print(f"Patient name : {appt_request.patient_name}")
    if appt_request.reason:
        print(f"Reason       : {appt_request.reason}")
    else:
        print("Reason       : (not specified)")
    print(
        "Date & time  : "
        f"{appt_request.start_dt.strftime('%Y-%m-%d %H:%M')} "
        f"to {appt_request.end_dt.strftime('%H:%M')} "
        f"{appt_request.start_dt.tzinfo}"
    )

    if not _confirm("Confirm and save this appointment to the calendar?"):
        print("Appointment not saved. You can start again if you like.")
        return

    try:
        event = create_appointment_event(
            service=service,
            patient_name=appt_request.patient_name,
            reason=appt_request.reason,
            start_dt=appt_request.start_dt,
            end_dt=appt_request.end_dt,
            calendar_id=appt_request.calendar_id,
        )
        link = event.get("htmlLink")
        print("\n✅ Appointment booked successfully!")
        if link:
            print(f"View it in Google Calendar: {link}")
    except Exception as e:
        print("❌ Error while creating the calendar event:")
        print(e)
