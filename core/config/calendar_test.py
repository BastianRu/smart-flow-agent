from datetime import datetime, timedelta

from .calendar_helpers import create_event, list_upcoming_events


def main():
    print('Listando próximos eventos...')
    events = list_upcoming_events(max_results=5)
    if not events:
        print('No se encontraron eventos.')
    else:
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(f"- {start} | {event.get('summary', 'Sin título')}")

    print('\nCreando un evento de prueba...')
    now = datetime.utcnow() + timedelta(minutes=10)
    created = create_event(
        summary='Evento de prueba desde Smartflow',
        start_datetime=now,
        end_datetime=now + timedelta(hours=1),
        description='Evento creado para probar la integración con Google Calendar.',
        location='Online',
    )
    print('Evento creado:')
    print(f"ID: {created.get('id')}")
    print(f"Resumen: {created.get('summary')}")
    print(f"Inicio: {created['start'].get('dateTime')}")
    print(f"Fin: {created['end'].get('dateTime')}")


if __name__ == '__main__':
    main()
