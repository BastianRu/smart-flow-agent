from datetime import datetime, timedelta
from email.utils import parseaddr

from core.config.google_cloud.google_cloud import get_calendar_service, log_and_raise_google_error
from google.auth.exceptions import RefreshError
from googleapiclient.errors import HttpError


def is_valid_email(email: str) -> bool:
    if not isinstance(email, str) or '@' not in email:
        return False
    _, addr = parseaddr(email)
    return bool(addr) and addr == email


def list_upcoming_events(calendar_id='primary', max_results=10):
    try:
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
    except Exception as exc:
        log_and_raise_google_error('list_upcoming_events', exc)


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
            print(f"[Calendar] invalid emails: {invalid_emails}")
            return {
                'error': 'validation_error',
                'message': 'La app no pudo completar la solicitud.',
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
        print(f"[Calendar] HTTP error: {e}")
        return {
            'error': 'calendar_api_error',
            'message': 'La app no pudo completar la solicitud.',
        }
    except RefreshError as e:
        print(f"[Calendar] Refresh error: {e}")
        raise RuntimeError('Google Calendar operation failed') from e
    except Exception as e:
        print(f"[Calendar] Unexpected error: {e}")
        raise RuntimeError('Google Calendar operation failed') from e
