from strands import tool
from core.config.calendar_helpers import create_event, list_upcoming_events
from core.session_context import add_tool_trace
from datetime import datetime

mock_projects = [
  {
    "id": "p1",
    "name": "Reserva del Valle",
    "location": "Zona Norte",
    "price": "$350,000,000 COP",
    "description": "Apartamentos de 2 y 3 habitaciones con salon social y piscina.",
    "detailed_info": {
      "areas": "Desde 72m² hasta 95m² de área construida.",
      "amenities": [
        "Piscina climatizada para adultos y niños",
        "Salón social de eventos tipo lounge",
        "Gimnasio semiequipado y zona de yoga",
        "Senderos peatonales y parque infantil"
      ],
      "specifications": "Acabados modernos de gama alta, cocina integral tipo americana con barra en granito, balcón amplio en la zona social, baño privado en la habitación principal y un parqueadero privado cubierto por apartamento.",
      "delivery_time": "Entrega estimada en el segundo semestre de 2027 (Etapa 1 en preventa).",
      "commercial_hook": "Ideal para familias que buscan confort, seguridad 24/7 y una alta valorización en un sector residencial exclusivo."
    }
  },
  {
    "id": "p2",
    "name": "Caminos del Bosque",
    "location": "Zona Norte",
    "price": "$200,000,000 COP",
    "description": "Apartamentos de 1 y 2 habitaciones con zona verde.",
    "detailed_info": {
      "areas": "Desde 48m² hasta 60m² con excelente distribución.",
      "amenities": [
        "Zonas verdes recreativas",
        "Zona de BBQ común al aire libre",
        "Biciparking seguro",
        "Parque para mascotas (Pet-friendly)"
      ],
      "specifications": "Diseño optimizado para iluminación natural, pisos en cerámica de alta resistencia, cocina semi-integral, zona de ropas independiente y parqueaderos comunes asignados por sorteo.",
      "delivery_time": "Entrega programada para finales de 2026 (Construcción avanzada).",
      "commercial_hook": "Perfecto para jóvenes profesionales, parejas o como inversión de alta rentabilidad para plataformas de alquiler de corta estancia debido a su entorno natural."
    }
  },
  {
    "id": "p3",
    "name": "Llanos de Calibio",
    "location": "Zona Norte",
    "price": "$150,000,000 COP",
    "description": "Apartamentos de 1 habitacion (55m2).",
    "detailed_info": {
      "areas": "Área única de 55m² tipo Loft o apartamento tradicional.",
      "amenities": [
        "Terraza comunal con vista panorámica de 360 grados",
        "Lavandería comunal tipo autoservicio",
        "Espacio de Coworking con internet de alta velocidad",
        "Vigilancia electrónica y portería permanente"
      ],
      "specifications": "Concepto abierto y funcional, acabados básicos de excelente calidad listos para personalizar, cocina con estufa empotrada, barra desayunadora, clóset empotrado y parqueadero exclusivo para motos.",
      "delivery_time": "Inmediata / En proyectos de planos para la Etapa 2 (12 meses).",
      "commercial_hook": "La opción más económica del mercado en la zona norte, ideal para independizarse, estudiantes universitarios o inversores tradicionales que buscan un flujo de caja rápido con arrendamientos tradicionales."
    }
  }
]

mock_appointments = [
  {
    "id": "a1",
    "customer_name": "Sebastian Ruiz",
    "customer_phone": "315 516 6455",
    "date": "15/07/2026",
    "hour": "9:00 AM",
    "project_id": "p1",
    "project_name": "Reserva del Valle",
    "description": "Apartamentos de 2 y 3 habitaciones con salon social y piscina."
  }
]

#Projects
@tool 
def get_projects():
  """Returns all projects currently available"""
  short_projects = [{ p["id"], p["name"], p["location"], p["price"], p["description"] } for p in mock_projects]
  add_tool_trace("get_projects", input_data=None, output_data=short_projects)
  return short_projects

@tool
def get_project_detail(project_id: str):
  """Returns the detailed information of a project. It takes the project id. Example: 'p1' """
  project_detail = [(p if p["id"] == project_id else None) for p in mock_projects]
  add_tool_trace("get_project_detail", input_data=project_id, output_data=project_detail)
  return project_detail

#appointment
@tool
def get_appointments():
  """Returns all the scheduled appointments until the date"""
  events_raw = list_upcoming_events(max_results=10)
  events = [e for e in events_raw]
  add_tool_trace("get_appointments", input_data=None, output_data=events)
  return events

@tool
def schedule_appointment( appointment: dict ):
  """Schedules a new appointment. Here's an example:
  {
    "id": "a1",
    "customer_name": "Sebastian Ruiz",
    "customer_email": "sebasr@gmail.com",
    "date": "15/07/2026" (MUST MATCH EXACTLY THIS FORMAT),
    "hour": "9:00 AM",
    "project_id": "p1",
    "project_name": "Reserva del Valle",
    "description": "Agendamiento de cita para cliente en el proyecto Reserva del Valle."
  }
  """
  created_raw = create_event(
    summary=f"{appointment['project_name']} | {appointment['customer_name']} | {appointment['hour']}",
    start_datetime=datetime.strptime(f"{appointment['date']} {appointment['hour']}", "%d/%m/%Y %I:%M %p"),
    description=f"{appointment['description']}",
    attendees=[appointment['customer_email']],
  )

  if isinstance(created_raw, dict) and created_raw.get('error'):
    result = {
      'error': created_raw['error'],
      'message': created_raw.get('message'),
      'invalid_emails': created_raw.get('invalid_emails'),
      'status_code': created_raw.get('status_code'),
      'requested_appointment': appointment,
    }
    add_tool_trace('schedule_appointment', input_data=appointment, output_data=result)
    return result

  created = {
    'id': created_raw.get('id'),
    'status': created_raw.get('status'),
    'summary': created_raw.get('summary'),
    'date': created_raw['start'].get('dateTime'),
    'hour': appointment['hour'],
    'customer_name': appointment['customer_name'],
    'customer_phone': appointment['customer_phone'],
  }
  add_tool_trace('schedule_appointment', input_data=appointment, output_data=created)
  return created


if __name__ == "__main__":
  created = schedule_appointment({
    "id": "a123",
    "customer_name": "Sebastian Ruiz",
    "customer_phone": "315 516 6455",
    "date": "15/09/2026",
    "hour": "9:00 AM",
    "project_id": "p123",
    "project_name": "Proyecto de prueba",
    "description": "Proyecto de Prueba."
  })
  print(created)

