from datetime import datetime, timedelta
from googleapiclient.discovery import build
from loguru import logger


class GoogleCalendar:
    def __init__(self, creds):
        self.service = build("calendar", "v3", credentials=creds)

    def get_events(self, days: int = 3) -> list[dict]:
        now = datetime.utcnow().isoformat() + "Z"
        end = (datetime.utcnow() + timedelta(days=days)).isoformat() + "Z"
        events_result = self.service.events().list(
            calendarId="primary",
            timeMin=now,
            timeMax=end,
            singleEvents=True,
            orderBy="startTime",
        ).execute()
        events = events_result.get("items", [])
        result = []
        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            result.append({
                "summary": event.get("summary", "No title"),
                "start": start,
                "end": event["end"].get("dateTime", event["end"].get("date")),
            })
        return result

    def create_event(self, summary: str, start_time: str, end_time: str, description: str = "") -> str:
        event = {
            "summary": summary,
            "description": description,
            "start": {"dateTime": start_time, "timeZone": "Asia/Kolkata"},
            "end": {"dateTime": end_time, "timeZone": "Asia/Kolkata"},
        }
        event = self.service.events().insert(calendarId="primary", body=event).execute()
        logger.info(f"Calendar event created: {summary}")
        return f"Created event: {summary} at {start_time}"

    def get_todays_events(self) -> str:
        events = self.get_events(days=1)
        if not events:
            return "No events scheduled today"
        parts = []
        for event in events:
            time = event["start"].split("T")[1][:5] if "T" in event["start"] else event["start"]
            parts.append(f"{time}: {event['summary']}")
        return "Today's events: " + ". ".join(parts)

    def update_event(self, event_id: str, summary: str = None, start_time: str = None, end_time: str = None) -> str:
        try:
            event = self.service.events().get(calendarId="primary", eventId=event_id).execute()
            if summary:
                event["summary"] = summary
            if start_time:
                event["start"]["dateTime"] = start_time
            if end_time:
                event["end"]["dateTime"] = end_time
            updated = self.service.events().update(calendarId="primary", eventId=event_id, body=event).execute()
            logger.info(f"Calendar event updated: {updated.get('summary', event_id)}")
            return f"Updated event: {updated.get('summary', event_id)}"
        except Exception as e:
            return f"Failed to update event: {e}"

    def cancel_event(self, event_id: str) -> str:
        try:
            self.service.events().delete(calendarId="primary", eventId=event_id).execute()
            logger.info(f"Calendar event cancelled: {event_id}")
            return f"Cancelled event {event_id}"
        except Exception as e:
            return f"Failed to cancel event: {e}"

    def find_free_slot(self, duration_minutes: int = 60, days: int = 5) -> str:
        events = self.get_events(days=days)
        working_start = 9
        working_end = 18
        for day_offset in range(days):
            day_start = datetime.utcnow().replace(hour=working_start, minute=0, second=0) + timedelta(days=day_offset)
            day_end = day_start.replace(hour=working_end)
            day_events = [e for e in events if day_start <= datetime.fromisoformat(e["start"].replace("Z", "")) <= day_end]
            current = day_start
            for event in day_events:
                event_start = datetime.fromisoformat(event["start"].replace("Z", ""))
                gap = (event_start - current).total_seconds() / 60
                if gap >= duration_minutes:
                    return f"Free slot found: {current.strftime('%A %I:%M %p')} for {duration_minutes} minutes"
                current = max(current, event_start)
            if (day_end - current).total_seconds() / 60 >= duration_minutes:
                return f"Free slot found: {current.strftime('%A %I:%M %p')} for {duration_minutes} minutes"
        return f"No free {duration_minutes}-minute slot found in the next {days} days"

    def set_reminder(self, event_id: str, minutes_before: int = 15) -> str:
        try:
            event = self.service.events().get(calendarId="primary", eventId=event_id).execute()
            event["reminders"] = {
                "useDefault": False,
                "overrides": [{"method": "popup", "minutes": minutes_before}],
            }
            self.service.events().update(calendarId="primary", eventId=event_id, body=event).execute()
            return f"Reminder set for {minutes_before} minutes before event"
        except Exception as e:
            return f"Failed to set reminder: {e}"
