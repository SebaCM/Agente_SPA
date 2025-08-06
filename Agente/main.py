import os
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
from typing import TypedDict, Literal
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.tools import tool, ToolException
from langgraph.graph import StateGraph, END

# --- 1. Configuración y Definición del Estado del Grafo ---

# Cargar la clave de API desde el archivo .env
load_dotenv()
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")

# Inicializa el LLM con el modelo especificado
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")

# Define los tipos de datos para el estado del grafo
class EmailClassificationState(TypedDict):
    """Estado del grafo para la clasificación de emails."""
    id: int
    subject: str
    email_text: str
    clasificacion: Literal["Solicitud de cita", "Consulta de precios/promociones", "Reclamo", "Feedback"]
    importancia: Literal["alta", "media", "baja"]
    tool_name: str

# --- 2. Herramientas del Grafo (Funciones de Acción) ---
# Se define cada acción como una herramienta con su propio esquema Pydantic
# para que el LLM pueda seleccionar la herramienta adecuada.

class CitaToolInput(BaseModel):
    id: int = Field(..., description="El ID del correo electrónico.")
    subject: str = Field(..., description="El asunto del correo electrónico.")
    email_text: str = Field(..., description="El texto completo del correo electrónico.")
    importancia: Literal["alta", "media", "baja"] = Field(..., description="La importancia asignada al correo.")

@tool(args_schema=CitaToolInput)
def handle_cita_tool(id: int, subject: str, email_text: str, importancia: Literal["alta", "media", "baja"]) -> dict:
    """
    Maneja los correos de solicitud de cita.
    Simula la impresión del evento en la consola.
    """
    print(f"--- Acción: Solicitud de Cita ---")
    print(f"Evento: Agendar cita para el correo con ID {id} y asunto '{subject}'.")
    return {"clasificacion": "Solicitud de cita", "importancia": importancia}

class PreciosToolInput(BaseModel):
    id: int = Field(..., description="El ID del correo electrónico.")
    subject: str = Field(..., description="El asunto del correo electrónico.")
    email_text: str = Field(..., description="El texto completo del correo electrónico.")
    importancia: Literal["alta", "media", "baja"] = Field(..., description="La importancia asignada al correo.")

@tool(args_schema=PreciosToolInput)
def handle_precios_tool(id: int, subject: str, email_text: str, importancia: Literal["alta", "media", "baja"]) -> dict:
    """
    Maneja los correos de consulta de precios.
    Simula el envío de una lista de precios atractiva.
    """
    print("--- Acción: Consulta de Precios ---")
    print(f"Respondiendo al correo con ID {id}:")
    print("""
    ¡Hola! Gracias por tu interés en nuestros servicios. Aquí está nuestra lista de precios:

    🧖‍♀️ Masaje Relajante: $80
    💆‍♂️ Facial Hidratante: $60
    💅 Manicure y Pedicure: $45
    ✨ Paquete Spa Completo: ¡Solo $150!

    Te esperamos en Spa Bella Luna para una experiencia inolvidable.
    """)
    return {"clasificacion": "Consulta de precios/promociones", "importancia": importancia}

class ReclamoToolInput(BaseModel):
    id: int = Field(..., description="El ID del correo electrónico.")
    subject: str = Field(..., description="El asunto del correo electrónico.")
    email_text: str = Field(..., description="El texto completo del correo electrónico.")
    importancia: Literal["alta", "media", "baja"] = Field(..., description="La importancia asignada al correo.")

@tool(args_schema=ReclamoToolInput)
def handle_reclamo_tool(id: int, subject: str, email_text: str, importancia: Literal["alta", "media", "baja"]) -> dict:
    """
    Maneja los correos de reclamo.
    Envía una notificación por email al gerente del spa.
    """
    remitente = os.getenv("GMAIL_USER")
    contraseña = os.getenv("GMAIL_PASS")
    destinatario = "seba1carrillo@gmail.com"
    servidor_smtp = "smtp.gmail.com"
    puerto_smtp = 587

    asunto = f"ALERTA: Reclamo Urgente del Correo #{id}"
    cuerpo = f"""
    Se ha recibido un reclamo urgente del correo con ID: {id}.
    identificador: {id}
    Asunto: {subject}
    Contenido:
    {email_text}

    Por favor, revisa este caso de inmediato.
    """

    mensaje = MIMEText(cuerpo)
    mensaje["Subject"] = asunto
    mensaje["From"] = remitente
    mensaje["To"] = destinatario

    print(f"--- Acción: Reclamo ---")
    try:
        if not remitente or not contraseña:
            print("Error: Las variables de entorno GMAIL_USER y GMAIL_PASS no están configuradas.")
            raise ValueError("Credenciales de email no encontradas.")

        with smtplib.SMTP(servidor_smtp, puerto_smtp) as server:
            server.starttls()
            server.login(remitente, contraseña)
            server.sendmail(remitente, destinatario, mensaje.as_string())
            print(f"Correo de reclamo enviado exitosamente a {destinatario}.")
    except Exception as e:
        print(f"Error al enviar el correo: {e}")
    
    return {"clasificacion": "Reclamo", "importancia": importancia}

class FeedbackToolInput(BaseModel):
    id: int = Field(..., description="El ID del correo electrónico.")
    subject: str = Field(..., description="El asunto del correo electrónico.")
    email_text: str = Field(..., description="El texto completo del correo electrónico.")
    importancia: Literal["alta", "media", "baja"] = Field(..., description="La importancia asignada al correo.")

@tool(args_schema=FeedbackToolInput)
def handle_feedback_tool(id: int, subject: str, email_text: str, importancia: Literal["alta", "media", "baja"]) -> dict:
    """
    Maneja los correos de feedback.
    Simula el guardado del mensaje en un archivo de testimonios.
    """
    testimonios_file = "testimonios.txt"
    with open(testimonios_file, "a", encoding="utf-8") as f:
        f.write(f"--- Testimonio de {datetime.now().strftime('%Y-%m-%d')} ---\n")
        f.write(f"Mensaje: {email_text}\n")
    print(f"--- Acción: Feedback ---")
    print(f"Testimonio del ID {id} guardado en '{testimonios_file}'.")
    return {"clasificacion": "Feedback", "importancia": importancia}

# Todas las herramientas disponibles para el LLM
tools = [handle_cita_tool, handle_precios_tool, handle_reclamo_tool, handle_feedback_tool]

# --- 3. Nodo del Grafo que Llama y Ejecuta la Herramienta ---

async def call_tool_node(state: EmailClassificationState) -> EmailClassificationState:
    """
    Este nodo utiliza el LLM para seleccionar y llamar a una de las herramientas de acción
    basándose en el contenido del correo electrónico.
    """
    # Enlaza las herramientas al LLM
    llm_with_tools = llm.bind_tools(tools)
    
    # Crea un prompt para guiar al LLM
    prompt_with_tools = PromptTemplate(
        template="""Eres un asistente de clasificación de emails para un spa. Tu tarea es analizar el correo proporcionado y, basándote en su contenido, seleccionar una de las siguientes herramientas para procesarlo. Es **obligatorio** que siempre selecciones una herramienta.

        Instrucciones:
        1. **Clasifica el correo**: ¿Es una "Solicitud de cita", "Consulta de precios/promociones", "Reclamo", o "Feedback"?
        2. **Asigna importancia**: 'alta' (para reclamos), 'media' (para solicitudes de cita), o 'baja' (para otros).
        3. **Selecciona la herramienta**: Elige la función de herramienta que coincida con la clasificación y pásale los argumentos correctos.
        id: {id}
        Asunto: "{subject}"
        Correo: "{email_text}"
        """,
        input_variables=["id","subject", "email_text"],
    )
    
    # Prepara el input para el LLM
    llm_input = {
        "id": state['id'],
        "subject": state['subject'],
        "email_text": state['email_text'],
    }
    
    # Invoca al LLM con las herramientas enlazadas
    ai_message = await llm_with_tools.ainvoke(prompt_with_tools.format(**llm_input))

    # Si el LLM seleccionó una herramienta, la ejecuta
    if ai_message.tool_calls:
        # Obtiene el nombre de la herramienta y los argumentos de la invocación
        tool_call = ai_message.tool_calls[0]
        tool_name = tool_call['name']
        tool_args = tool_call['args']
        
        chosen_tool = next((t for t in tools if t.name == tool_name), None)
        if not chosen_tool:
            raise ToolException(f"Herramienta '{tool_name}' no encontrada.")
        
        result = await chosen_tool.ainvoke(tool_args)
        
        # Actualiza el estado con los resultados de la herramienta
        state['clasificacion'] = result.get("clasificacion")
        state['importancia'] = result.get("importancia")
        state['tool_name'] = tool_name
    else:
        # Si no se selecciona ninguna herramienta, se genera un error claro
        raise ValueError("El modelo de lenguaje no pudo seleccionar una herramienta adecuada para el correo.")
        
    return state

# --- 4. Construcción y Compilación del Grafo ---

def build_graph():
    """Crea y compila el grafo de LangGraph."""
    workflow = StateGraph(EmailClassificationState)
    
    # El único nodo del grafo es el que llama y ejecuta la herramienta
    workflow.add_node("call_tool_node", call_tool_node)
    
    workflow.set_entry_point("call_tool_node")
    workflow.add_edge("call_tool_node", END)
    
    return workflow.compile()

email_classifier_graph = build_graph()

# --- 5. Aplicación de FastAPI y Endpoints ---

app = FastAPI(
    title="Spa AI Email Classifier",
    description="API para clasificar emails de clientes de un spa usando LangGraph y Gemini-Pro.",
    version="1.0"
)

# Definimos el modelo de Pydantic para la solicitud
class EmailRequest(BaseModel):
    id: int
    subject: str
    email_text: str

# Definimos el modelo de Pydantic para la respuesta
class ClassificationResponse(BaseModel):
    id: int
    subject: str
    email_text: str
    clasificacion: Literal["Solicitud de cita", "Consulta de precios/promociones", "Reclamo", "Feedback"] = Field(
        ...,
        description="La clasificación del correo electrónico, como 'Solicitud de cita', 'Consulta de precios/promociones', 'Reclamo', o 'Feedback'."
    )
    importancia: Literal["alta", "media", "baja"] = Field(
        ...,
        description="La importancia del correo electrónico, como 'alta', 'media', o 'baja'."
    )

@app.post("/classify-email", response_model=ClassificationResponse)
async def classify_email_endpoint(email_request: EmailRequest):
    """
    Recibe un solo correo electrónico, lo clasifica y detona una acción.
    Devuelve la clasificación y la importancia.
    """
    try:
        initial_state = {
            'id': email_request.id,
            'subject': email_request.subject,
            'email_text': email_request.email_text,
            'clasificacion': '', # Se inicializa vacío
            'importancia': '', # Se inicializa vacío
            'tool_name': ''
        }
        
        final_state = await email_classifier_graph.ainvoke(initial_state)
        
        return ClassificationResponse(
            id=final_state['id'],
            subject=final_state['subject'],
            email_text=final_state['email_text'],
            clasificacion=final_state['clasificacion'],
            importancia=final_state['importancia']
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
