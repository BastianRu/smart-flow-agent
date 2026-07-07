from datetime import datetime, timedelta

from core.config.google_cloud import get_calendar_service
from google.auth.exceptions import RefreshError


def list_upcoming_events(calendar_id='primary', max_results=10):
    service = get_calendar_service()
    now = datetime.utcnow().isoformat() + 'Z'
    events_result = service.events().list(
        calendarId=calendar_id,
        timeMin=now,
        maxResults=max_results,
        singleEvents=True,
        orderBy='startTime',
    ).execute()
    events = events_result.get('items', [])
    return events


def create_event(
    summary,
    start_datetime,
    end_datetime=None,
    description=None,
    location=None,
    attendees=None,
    calendar_id='primary',
    time_zone='America/Bogota',
):
    service = get_calendar_service()
    if end_datetime is None:
        end_datetime = start_datetime + timedelta(hours=1)

    event = {
        'summary': summary,
        'start': {'dateTime': start_datetime.isoformat(), 'timeZone': time_zone},
        'end': {'dateTime': end_datetime.isoformat(), 'timeZone': time_zone},
    }
    if description:
        event['description'] = description
    if location:
        event['location'] = location
    if attendees:
        event['attendees'] = [{'email': email} for email in attendees]

    try:
        created_event = service.events().insert(calendarId=calendar_id, body=event).execute()
        return created_event
    except RefreshError as e:
        # Normalize error for callers (agent) so they can prompt re-auth
        raise RuntimeError('Authorization refresh failed; re-authorize the app by running get_tokens.py') from e
