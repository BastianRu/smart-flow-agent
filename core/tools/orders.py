import copy
from strands import tool

# GET /api/producto
MOCK_PRODUCTS = [
    {
        "id": "prod-001",
        "nombre": "Hamburguesa Clásica",
        "precio": 18500,
        "stock": 15,
        "status": "active",  # O 'low_stock', 'out_of_stock'
        "categoria": {
            "nombre": "Hamburguesas"
        }
    },
    {
        "id": "prod-002",
        "nombre": "Papas Fritas",
        "precio": 7000,
        "stock": 3,
        "status": "low_stock",
        "categoria": {
            "nombre": "Acompañamientos"
        }
    }
]

# POST /api/cliente/find-or-create
MOCK_CLIENTE_RESPONSE = {
    "cliente": {
        "id": "cli-8839",
        "nombre": "Juan Sebastián",
        "telefono": "3001234567",
        "email": "juan@example.com",
        "direccionPrincipal": "Calle 10 #2-34"
    },
    "esNuevo": False  # Determina si el bot dice "¡Bienvenido!" o "¡Bienvenido de nuevo!"
}

# GET /api/cliente/telefono/{telefono}
MOCK_CUSTOMER_BY_PHONE = {
    "id": "cli-8839",
    "nombre": "Juan Sebastián",
    "telefono": "3001234567"
}

# POST /api/pedido Y GET /api/pedido/{pedidoId}
PEDIDO_MOCK = {
    "id": "ped-99421-xyz",
    "estado": "PENDIENTE",  # Valores válidos: PENDIENTE, CONFIRMADO, EN_PREPARACION, EN_CAMINO, ENTREGADO, CANCELADO
    "total": 44000,
    "direccion": "Calle 10 #2-34",
    "metodoPago": "EFECTIVO",
    "items": [
        {
            "cantidad": 2,
            "producto": {
                "nombre": "Hamburguesa Clásica"
            }
        },
        {
            "cantidad": 1,
            "producto": {
                "nombre": "Papas Fritas"
            }
        }
    ]
}

# GET /api/pedido/usuario/{clienteId}
HISTORIAL_PEDIDOS_MOCK = [
    {
        "id": "ped-99421-xyz",  # El más reciente
        "estado": "EN_PREPARACION",
        "total": 25500,
        "direccion": "Calle 10 #2-34",
        "metodoPago": "EFECTIVO",
        "items": [
            {
                "cantidad": 1,
                "producto": {"nombre": "Hamburguesa Clásica"}
            }
        ]
    },
    {
        "id": "ped-00121-abc",  # Pedido antiguo
        "estado": "ENTREGADO",
        "total": 7000,
        "direccion": "Calle 10 #2-34",
        "metodoPago": "TRANSFERENCIA",
        "items": [
            {
                "cantidad": 1,
                "producto": {"nombre": "Papas Fritas"}
            }
        ]
    }
]


@tool
def get_products() -> list:
    """Obtiene el catálogo de productos desde el endpoint `GET /api/producto`.

    Retorna una lista de productos. Cada producto contiene los campos:
    - `id`: identificador del producto
    - `nombre`: nombre legible
    - `precio`: precio en centavos o la unidad monetaria usada
    - `stock`: cantidad disponible
    - `status`: estado comercial (por ejemplo, `active`, `low_stock`, `out_of_stock`)
    - `categoria`: objeto con información de categoría

    Returns:
        list: Lista de diccionarios con la información de productos.
    """
    return copy.deepcopy(MOCK_PRODUCTS)


@tool
def find_or_create_customer(cliente: dict) -> dict:
    """Registra o recupera un cliente mediante `POST /api/cliente/find-or-create`.

    Parámetros esperados en `cliente`:
    - `nombre` (str)
    - `telefono` (str)
    - `email` (str, opcional)
    - `direccionPrincipal` (str, opcional)

    Returns:
        dict: Objeto con la clave `cliente` que contiene los datos del cliente y
              `esNuevo` (bool) indicando si fue creado o ya existía.
    """
    telefono = str(cliente.get("telefono", ""))
    if telefono == MOCK_CLIENTE_RESPONSE["cliente"]["telefono"]:
        return copy.deepcopy(MOCK_CLIENTE_RESPONSE)

    nuevo_cliente = {
        "cliente": {
            "id": "cli-9999",
            "nombre": cliente.get("nombre", "Cliente Nuevo"),
            "telefono": telefono,
            "email": cliente.get("email", ""),
            "direccionPrincipal": cliente.get("direccionPrincipal", "")
        },
        "esNuevo": True
    }
    return nuevo_cliente


@tool
def get_customer_by_phone(telefono: str) -> dict:
    """Recupera la información de un cliente por teléfono vía `GET /api/cliente/telefono/{telefono}`.

    Args:
        telefono (str): Número de teléfono del cliente a buscar.

    Returns:
        dict: Datos del cliente si se encuentra, o un diccionario con clave `error` si no existe.
    """
    telefono = str(telefono)
    if telefono == MOCK_CUSTOMER_BY_PHONE["telefono"]:
        return copy.deepcopy(MOCK_CUSTOMER_BY_PHONE)
    return {"error": "Cliente no encontrado", "telefono": telefono}


@tool
def create_order(pedido: dict) -> dict:
    """Crea un pedido a través de `POST /api/pedido` y retorna los detalles del mismo.

    Parámetros esperados en `pedido` (ejemplos):
    - `id` (str, opcional): identificador del pedido
    - `direccion` (str)
    - `metodoPago` (str)
    - `total` (num)
    - `items` (list): lista de ítems con `cantidad` y `producto`

    Returns:
        dict: Representación del pedido con su estado y los campos proporcionados.
    """
    resultado = copy.deepcopy(PEDIDO_MOCK)
    resultado["estado"] = "PENDIENTE"

    if "id" in pedido:
        resultado["id"] = pedido["id"]
    if "direccion" in pedido:
        resultado["direccion"] = pedido["direccion"]
    if "metodoPago" in pedido:
        resultado["metodoPago"] = pedido["metodoPago"]
    if "total" in pedido:
        resultado["total"] = pedido["total"]
    if "items" in pedido:
        resultado["items"] = pedido["items"]

    return resultado


@tool
def get_order(pedido_id: str) -> dict:
    """Recupera los detalles de un pedido por su ID mediante `GET /api/pedido/{pedidoId}`.

    Args:
        pedido_id (str): Identificador del pedido.

    Returns:
        dict: Objeto con los detalles del pedido o un diccionario con clave `error` si no se encuentra.
    """
    if str(pedido_id) == PEDIDO_MOCK["id"]:
        return copy.deepcopy(PEDIDO_MOCK)
    return {"error": "Pedido no encontrado", "pedidoId": pedido_id}


@tool
def get_order_history(cliente_id: str) -> list:
    """Obtiene el historial de pedidos de un cliente vía `GET /api/pedido/usuario/{clienteId}`.

    Args:
        cliente_id (str): Identificador del cliente.

    Returns:
        list: Lista de pedidos asociados al cliente ordenada por fecha (más reciente primero).
    """
    if str(cliente_id) == MOCK_CLIENTE_RESPONSE["cliente"]["id"]:
        return copy.deepcopy(HISTORIAL_PEDIDOS_MOCK)
    return []

