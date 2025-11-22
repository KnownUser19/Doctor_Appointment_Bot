
# app.py

from calendar_utils_live import get_calendar_service
from dialog_manager import run_conversation


def main():
    print("Starting Doctor Appointment Booking Bot...")
    service = get_calendar_service()

    while True:
        run_conversation(service)
        again = input("\nWould you like to book another appointment? (y/n): ").strip().lower()
        if again not in ("y", "yes"):
            print("Goodbye! Stay healthy. 👋")
            break


if __name__ == "__main__":
    main()
