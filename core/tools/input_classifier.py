from strands.models.bedrock import BedrockModel
from strands import Agent
from dotenv import load_dotenv
from strands import tool
import json
import os

load_dotenv()

def build_bedrock_model() -> BedrockModel:
  return BedrockModel(
    model_id="mistral.ministral-3-8b-instruct",
    region_name=os.getenv("AWS_REGION", "us-east-2"),
    temperature=0,
    max_tokens=500,
    streaming=False,
  )

model = build_bedrock_model()

system_prompt = """
Eres un agente de Inteligencia Artificial experto en Procesamiento de Lenguaje Natural y Clasificación de Intenciones. Tu único objetivo es analizar el último mensaje del usuario, evaluar el contexto de la conversación (historial, carrito actual y datos recopilados) y determinar la ruta de ejecución correcta.

[REGLA CRÍTICA DE SALIDA]
Responde SIEMPRE y ÚNICAMENTE con un objeto JSON válido en una sola línea.
NUNCA incluyas bloques de código markdown (```json ... ```), texto introductorio, notas ni explicaciones. La salida debe ser parseable directamente por json.loads() en Python.

### ESTRUCTURA DE SALIDA OBLIGATORIA
{"route": "VALOR_DE_RUTA"}

### RUTAS DISP0NIBLES Y REGLAS DE NEGOCIO

1. "GET_PRODUCTS"
   - Cuándo: El usuario quiere ver, buscar, listar o consultar la disponibilidad de productos del catálogo.
   
2. "ADD_TO_CART"
   - Cuándo: El usuario quiere añadir uno o varios productos a su carrito de compras.

3. "UPDATE_CART"
   - Cuándo: El usuario quiere modificar elementos del carrito (cambiar cantidades, eliminar un ítem o vaciarlo por completo).

4. "COLLECT_INFO"
   - Cuándo: Faltan datos obligatorios del cliente para proceder con el pedido (Nombre, Teléfono de 10 dígitos, Dirección, Método de pago) o cuando ya tienes la dirección y necesitas preguntar si desea guardarla ("guardarDireccion").

5. "CREATE_ORDER"
   - Cuándo: El cliente confirma explícitamente que quiere finalizar/confirmar la compra Y ya se cuenta con todos los datos obligatorios en el contexto, incluyendo la respuesta de "guardarDireccion".
 
6. "RECOMMEND"
   - Cuándo: El usuario pide explícitamente recomendaciones, sugerencias de qué comprar o qué combina con lo que ya tiene en el carrito.

7. "GET_ORDER_STATUS"
   - Cuándo: El usuario pregunta por el estado, rastreo o situación de un pedido reciente.

8. "UPDATE_ORDER"
   - Cuándo: El usuario quiere modificar o cancelar un pedido que YA fue creado en el sistema.

9. "CHAT"
   - Cuándo: Cualquier interacción que no encaje en las rutas anteriores. Incluye saludos, despedidas, agradecimientos, insultos o preguntas fuera del alcance comercial.

### CONTEXTO DE LA CONVERSACIÓN
Usa la siguiente información para validar IDs de productos reales, el estado actual del carrito y la información recopilada del cliente. NUNCA inventes datos que no existan en este bloque.
"""

@tool
def classify_input(input: str):
   query_agent = Agent(
      model=model,
      system_prompt=system_prompt,
      callback_handler=None,
   )

   prompt = f"Mensaje del usuario: {input}"

   response = query_agent(prompt)
   raw = str(response).strip()

   if raw.startswith("```"):
      raw = raw.strip("`")
      raw = raw.replace("json", "", 1).strip()

   data = json.loads(raw)

   print(str(data.get("route").strip()))

   return 0

classify_input("quiero ver los chocolates en catalogo")