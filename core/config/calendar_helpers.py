from datetime import datetime, timedelta
from email.utils import parseaddr

from core.config.google_cloud import get_calendar_service
from google.auth.exceptions import RefreshError
from googleapiclient.errors import HttpError


def is_valid_email(email: str) -> bool:
    if not isinstance(email, str) or '@' not in email:
        return False
    _, addr = parseaddr(email)
    return bool(addr) and addr == email


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
        if isinstance(attendees, str):
            attendees = [attendees]
        invalid_emails = [address for address in attendees if not is_valid_email(address)]
        if invalid_emails:
            return {
                'error': 'invalid_email',
                'invalid_emails': invalid_emails,
                'message': f"Correo inválido: {', '.join(invalid_emails)}",
            }
        event['attendees'] = [{'email': attendee_email} for attendee_email in attendees]

    try:
        created_event = service.events().insert(
            calendarId=calendar_id,
            body=event,
            sendUpdates='all',
        ).execute()
        return created_event
    except HttpError as e:
        return {
            'error': 'calendar_api_error',
            'message': str(e),
            'status_code': getattr(e.resp, 'status', None),
        }
    except RefreshError as e:
        # Normalize error for callers (agent) so they can prompt re-auth
        raise RuntimeError('Authorization refresh failed; re-authorize the app by running get_tokens.py') from e
