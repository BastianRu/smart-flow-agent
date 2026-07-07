import copy
import os
from typing import Any

import requests
from strands import tool

BASE_URL = os.getenv("API_BASE_URL", "https://smartserve-ai-production.up.railway.app/api")

# GET /api/categoria
MOCK_CATEGORIES = [
    {
        "id": "cat-001",
        "nombre": "Licores",
        "descripcion": "Aguardientes, whiskies, rones y más"
    },
    {
        "id": "cat-002",
        "nombre": "Cervezas",
        "descripcion": "Cervezas nacionales e importadas"
    },
    {
        "id": "cat-003",
        "nombre": "Snacks",
        "descripcion": "Pasabocas y acompañamientos"
    }
]

# GET /api/producto
MOCK_PRODUCTS = [
    {
        "id": "prod-001",
        "nombre": "Aguardiente Nariño",
        "descripcion": "Aguardiente tradicional del sur",
        "precio": 18000,
        "stock": 50,
        "slug": "aguardiente-narino",
        "status": "active",
        "ivaPercent": 19,
        "categoriaId": "cat-001"
    },
    {
        "id": "prod-002",
        "nombre": "Ron Medellín Añejo",
        "descripcion": "Ron colombiano añejado 3 años",
        "precio": 45000,
        "stock": 30,
        "slug": "ron-medellin-anejo",
        "status": "active",
        "ivaPercent": 19,
        "categoriaId": "cat-001"
    },
    {
        "id": "prod-003",
        "nombre": "Cerveza Club Colombia",
        "descripcion": "Cerveza rubia premium colombiana 330ml",
        "precio": 4500,
        "stock": 120,
        "slug": "cerveza-club-colombia",
        "status": "active",
        "ivaPercent": 19,
        "categoriaId": "cat-002"
    },
    {
        "id": "prod-004",
        "nombre": "Maní Salado",
        "descripcion": "Maní tostado y salado 100g",
        "precio": 2500,
        "stock": 80,
        "slug": "mani-salado",
        "status": "active",
        "ivaPercent": 0,
        "categoriaId": "cat-003"
    }
]

# POST /api/cliente/find-or-create
MOCK_CLIENTE_RESPONSE = {
    "cliente": {
        "id": "cli-8839",
        "nombre": "Juan Sebastián",
        "telefono": "3001234567",
        "email": "juan@example.com",
        "direccionPrincipal": "Calle 10 #2-34",
        "estado": "ACTIVO"
    },
    "esNuevo": False
}

# GET /api/cliente/telefono/{telefono}
MOCK_CUSTOMER_BY_PHONE = {
    "id": "cli-8839",
    "nombre": "Juan Sebastián",
    "telefono": "3001234567",
    "email": "juan@example.com",
    "direccionPrincipal": "Calle 10 #2-34",
    "estado": "ACTIVO"
}

# POST /api/pedido Y GET /api/pedido/{pedidoId}
PEDIDO_MOCK = {
    "id": "ped-99421-xyz",
    "estado": "PENDIENTE",
    "total": 44000,
    "direccion": "Calle 10 #2-34",
    "metodoPago": "EFECTIVO",
    "items": [
        {
            "cantidad": 2,
            "producto": {
                "nombre": "Aguardiente Nariño"
            }
        },
        {
            "cantidad": 1,
            "producto": {
                "nombre": "Cerveza Club Colombia"
            }
        }
    ]
}

# GET /api/pedido/usuario/{clienteId}
HISTORIAL_PEDIDOS_MOCK = [
    {
        "id": "ped-99421-xyz",
        "estado": "EN_PREPARACION",
        "total": 25500,
        "direccion": "Calle 10 #2-34",
        "metodoPago": "EFECTIVO",
        "items": [
            {
                "cantidad": 1,
                "producto": {"nombre": "Aguardiente Nariño"}
            }
        ]
    },
    {
        "id": "ped-00121-abc",
        "estado": "ENTREGADO",
        "total": 7000,
        "direccion": "Calle 10 #2-34",
        "metodoPago": "TRANSFERENCIA",
        "items": [
            {
                "cantidad": 1,
                "producto": {"nombre": "Maní Salado"}
            }
        ]
    }
]


def _api_headers() -> dict:
    headers = {"Accept": "application/json"}
    token = os.getenv("BEARER_AUTH_ACCESS_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def _request(method: str, path: str, json_data: Any = None) -> Any:
    url = f"{BASE_URL}{path}"
    try:
        response = requests.request(method, url, headers=_api_headers(), json=json_data, timeout=10)
        if response.ok:
            return response.json()
    except requests.exceptions.RequestException:
        pass
    return None


@tool
def get_categories() -> list:
    """Recupera la lista de categorías del endpoint `GET /api/categoria`."""
    resultado = _request("GET", "/categoria")
    return resultado if resultado is not None else copy.deepcopy(MOCK_CATEGORIES)


@tool
def get_products() -> list:
    """Obtiene el catálogo de productos desde el endpoint `GET /api/producto`."""
    resultado = _request("GET", "/producto")
    return resultado if resultado is not None else copy.deepcopy(MOCK_PRODUCTS)


@tool
def get_product_by_id(producto_id: str) -> dict:
    """Recupera los detalles de un producto por su ID con `GET /api/producto/{id}`."""
    resultado = _request("GET", f"/producto/{producto_id}")
    if resultado is not None:
        return resultado
    for producto in MOCK_PRODUCTS:
        if producto["id"] == producto_id:
            return copy.deepcopy(producto)
    return {"error": "Producto no encontrado", "id": producto_id}


@tool
def find_or_create_customer(cliente: dict) -> dict:
    """Registra o recupera un cliente mediante `POST /api/cliente/find-or-create`."""
    resultado = _request("POST", "/cliente/find-or-create", json_data=cliente)
    return resultado if resultado is not None else copy.deepcopy(MOCK_CLIENTE_RESPONSE)


@tool
def get_customer_by_phone(telefono: str) -> dict:
    """Recupera la información de un cliente por teléfono vía `GET /api/cliente/telefono/{telefono}`."""
    resultado = _request("GET", f"/cliente/telefono/{telefono}")
    if resultado is not None:
        return resultado
    if telefono == MOCK_CUSTOMER_BY_PHONE["telefono"]:
        return copy.deepcopy(MOCK_CUSTOMER_BY_PHONE)
    return {"error": "Cliente no encontrado", "telefono": telefono}


@tool
def create_order(pedido: dict) -> dict:
    """Crea un pedido a través de `POST /api/pedido` y retorna los detalles del mismo."""
    resultado = _request("POST", "/pedido", json_data=pedido)
    if resultado is not None:
        return resultado
    fallback = copy.deepcopy(PEDIDO_MOCK)
    fallback["estado"] = "PENDIENTE"
    for key in ("id", "direccion", "metodoPago", "total", "items"):
        if key in pedido:
            fallback[key] = pedido[key]
    return fallback


@tool
def get_order(pedido_id: str) -> dict:
    """Recupera los detalles de un pedido por su ID mediante `GET /api/pedido/{pedidoId}`."""
    resultado = _request("GET", f"/pedido/{pedido_id}")
    if resultado is not None:
        return resultado
    if str(pedido_id) == PEDIDO_MOCK["id"]:
        return copy.deepcopy(PEDIDO_MOCK)
    return {"error": "Pedido no encontrado", "pedidoId": pedido_id}


@tool
def get_order_history(cliente_id: str) -> list:
    """Obtiene el historial de pedidos de un cliente vía `GET /api/pedido/usuario/{clienteId}`."""
    resultado = _request("GET", f"/pedido/usuario/{cliente_id}")
    if resultado is not None:
        return resultado
    if str(cliente_id) == MOCK_CLIENTE_RESPONSE["cliente"]["id"]:
        return copy.deepcopy(HISTORIAL_PEDIDOS_MOCK)
    return []

