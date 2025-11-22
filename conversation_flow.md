
# Conversation Flow – Doctor Appointment Booking Bot

## High-Level Flow

1. **Start**
   - Bot greets the user.

2. **Collect Patient Info**
   - Ask: "Your full name?"
   - Ask: "Reason for visit (optional)?"

3. **Collect Preference**
   - Ask: "Preferred date (YYYY-MM-DD)?"
     - If invalid format → explain → re-ask.
     - If in the past → explain → re-ask.
   - Ask: "Preferred time (HH:MM, 24h)?"
     - If invalid format → explain → re-ask.

4. **Check Slot Availability**
   - Build timezone-aware start/end datetime.
   - Call `is_slot_available(...)`:
     - **If available:**
       - Inform the user:
         - “This time is available.”
       - Ask for confirmation:
         - If confirmed → create event → success message.
         - If not confirmed → go to “Suggest Next Slots”.
     - **If not available:**
       - Inform the user of the conflict.
       - Proceed to “Suggest Next Slots”.

5. **Suggest Next Available Slots**
   - Call `find_next_available_slots(...)` (up to 3 within next X days).
   - If **no slots found**:
     - Apologize and ask the user to try a different date.
   - If **slots available**:
     - Show a numbered list of options.
     - Option “0” = Cancel.
     - Ask the user to pick a slot number:
       - 0 → cancel.
       - Valid number → update appointment request with chosen slot.

6. **Final Confirmation & Booking**
   - Show summary:
     - Patient name.
     - Reason.
     - Date/time range and timezone.
   - Ask: “Confirm and save this appointment?”
     - If yes → call `create_appointment_event(...)` → success message + event link.
     - If no → end without saving.

7. **Repeat or Exit**
   - Ask: “Book another appointment? (y/n)”
   - If yes → restart at step 2.
   - If no → exit with goodbye message.

## Diagram (Text)

```text
Start
  |
  v
Greet user
  |
  v
Collect name & reason
  |
  v
Ask preferred date ----> invalid / past? ----> re-ask
  |
  v
Ask preferred time ----> invalid? -----------> re-ask
  |
  v
Build start/end datetime
  |
  v
Check calendar availability
  |-----------------------------|
  |                             |
  v                             v
Slot available?           Slot NOT available
  |                             |
  v                             v
Ask user to confirm        Inform conflict
  |                             |
  | yes                         |
  v                             |
Create event & success          |
  |                             |
  v                             |
 Ask to book another            |
                                v
                      Suggest next slots
                                |
                 no slots ------|------ some slots
                (apologize)            |
                                        v
                              Show slot options
                                |
                      user chooses or cancels
                                |
                         cancel? ----> end
                                |
                                v
                       Update appointment time
                                |
                                v
                        Final confirmation
                         |           |
                        yes         no
                         |           |
                         v           v
                    Create event     end
                         |
                         v
                 Ask to book another
