
# Doctor Appointment Booking Bot (Google Calendar)

A simple CLI-based assistant that books doctor appointments directly into **Google Calendar**.

The bot:

- Talks to the user in the terminal
- Collects patient name, reason, preferred date & time
- Checks Google Calendar for conflicts
- Suggests the next available slots when needed
- Creates a real event in Google Calendar once confirmed

---

<p align="center">
  <img src="[https://raw.githubusercontent.com/<your-username>/<repo-name>/main/assets/doctor-cover.png](https://drive.google.com/file/d/1mw_1WX5V0Myy7LeH9qgEC-dbk9AvnKI9/view?usp=sharing)" width="100%">
</p>


## 1. Tech Stack

- Python 3.9+
- Google Calendar API (OAuth 2.0)
- Libraries:
  - `google-api-python-client`
  - `google-auth-oauthlib`
  - `google-auth-httplib2`
  - `pytz`

---

## 2. Project Structure

```text
app.py                   # entry point
dialog_manager.py        # conversation logic and flow
calendar_utils_live.py   # real Google Calendar integration
calendar_utils.py        # demo/offline calendar (no API)
config.py                # timezone, work hours, defaults
conversation_flow.md     # written description of flow
requirements.txt         # Python dependencies
demo/
  screenshot_cli_booking.png
  screenshot_calendar.png
  demo_video_link.txt    # link to screen recording 



