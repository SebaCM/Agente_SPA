import os
import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timedelta
from typing import TypedDict, Literal, Optional
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
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
    date: str  # Nuevo campo para la fecha del correo
    clasificacion: Literal["Solicitud de cita", "Consulta de precios/promociones", "Reclamo", "Feedback"]
    importancia: Literal["alta", "media", "baja"]
    tool_name: str
    mensaje: Optional[str]

# --- 2. Herramientas del Grafo (Funciones de Acción) ---

class CitaToolInput(BaseModel):
    id: int = Field(..., description="El ID del correo electrónico.")
    subject: str = Field(..., description="El asunto del correo electrónico.")
    email_text: str = Field(..., description="El texto completo del correo electrónico.")
    importancia: Literal["alta", "media", "baja"] = Field(..., description="La importancia asignada al correo.")

@tool(args_schema=CitaToolInput)
def handle_cita_tool(id: int, subject: str, email_text: str, importancia: Literal["alta", "media", "baja"]) -> dict:
    """
    Maneja los correos de solicitud de cita.
    """
    print(f"--- Acción: Solicitud de Cita ---")
    print(f"Evento: Agendar cita para el correo con ID {id} y asunto '{subject}'.")
    return {"clasificacion": "Solicitud de cita", "importancia": importancia, "mensaje": None}

class PreciosToolInput(BaseModel):
    id: int = Field(..., description="El ID del correo electrónico.")
    subject: str = Field(..., description="El asunto del correo electrónico.")
    email_text: str = Field(..., description="El texto completo del correo electrónico.")
    importancia: Literal["alta", "media", "baja"] = Field(..., description="La importancia asignada al correo.")

@tool(args_schema=PreciosToolInput)
def handle_precios_tool(id: int, subject: str, email_text: str, importancia: Literal["alta", "media", "baja"]) -> dict:
    """
    Maneja los correos de consulta de precios y retorna el mensaje.
    """
    mensaje = """
    ¡Hola! Gracias por tu interés en nuestros servicios. Aquí está nuestra lista de precios:

    🧖‍♀️ Masaje Relajante: $80
    💆‍♂️ Facial Hidratante: $60
    💅 Manicure y Pedicure: $45
    ✨ Paquete Spa Completo: ¡Solo $150!

    Te esperamos en Spa Bella Luna para una experiencia inolvidable.
    """
    print("--- Acción: Consulta de Precios ---")
    print(f"Respondiendo al correo con ID {id}:")
    print(mensaje)
    return {"clasificacion": "Consulta de precios/promociones", "importancia": importancia, "mensaje": mensaje}

class ReclamoToolInput(BaseModel):
    id: int = Field(..., description="El ID del correo electrónico.")
    subject: str = Field(..., description="El asunto del correo electrónico.")
    email_text: str = Field(..., description="El texto completo del correo electrónico.")
    date: str= Field(..., description="La fecha en que se recibió el correo, en formato YYYY-MM-DD.")
    importancia: Literal["alta", "media", "baja"] = Field(..., description="La importancia asignada al correo.")


@tool(args_schema=ReclamoToolInput)
def handle_reclamo_tool(id: int, subject: str, email_text: str, date: str, importancia: Literal["alta", "media", "baja"]) -> dict:
    """
    Maneja los correos de reclamo y envía una notificación por email.
    Las direcciones de correo se obtienen de las variables de entorno.
    """
    remitente = os.getenv("GMAIL_USER")
    contraseña = os.getenv("GMAIL_PASS")
    destinatario="seba1carrillo@gmail.com"
    #destinatario = os.getenv("RECLAMO_RECIPIENT_EMAIL")
    #destinatarios_cc = os.getenv("RECLAMO_CC_EMAILS", "").split(',')
    
    servidor_smtp = "smtp.gmail.com"
    puerto_smtp = 587

    # Lógica para construir el asunto dentro de la herramienta
    try:
        email_date = datetime.strptime(date, '%Y-%m-%d')
        today = datetime.now()
        age_in_days = (today - email_date).days
        new_subject = f"ALERTA: Reclamo Urgente del Correo #{id} ya han pasado {age_in_days} dias"
        
    except (ValueError, KeyError) as e:
        print(f"ADVERTENCIA: No se pudo modificar el asunto del reclamo. Error: {e}")
        new_subject = f"ALERTA: Reclamo Urgente del Correo #{id}" # Asunto de fallback


    cuerpo = f"""
    Se ha recibido un reclamo urgente del correo con ID: {id}.

    Asunto original: {subject}
    Contenido:
    {email_text}

    Por favor, revisa este caso de inmediato.
    """

    mensaje = MIMEText(cuerpo)
    mensaje["Subject"] = new_subject
    mensaje["From"] = remitente
    mensaje["To"] = destinatario
    
    if destinatarios_cc:
        mensaje["Cc"] = ",".join(destinatarios_cc)

    print(f"--- Acción: Reclamo ---")
    try:
        if not remitente or not contraseña:
            print("Error: Las variables de entorno GMAIL_USER y GMAIL_PASS no están configuradas.")
            raise ValueError("Credenciales de email no encontradas.")
        
        if not destinatario:
            print("Error: El destinatario del reclamo no está configurado en las variables de entorno.")
            raise ValueError("Destinatario de reclamo no encontrado.")

        with smtplib.SMTP(servidor_smtp, puerto_smtp) as server:
            server.starttls()
            server.login(remitente, contraseña)
            recipients = [destinatario] + destinatarios_cc
            server.sendmail(remitente, recipients, mensaje.as_string())
            print(f"Correo de reclamo enviado exitosamente a {destinatario} y CC a {', '.join(destinatarios_cc)}.")
    except Exception as e:
        print(f"Error al enviar el correo: {e}")
    
    return {"clasificacion": "Reclamo", "importancia": importancia, "mensaje": None}

class FeedbackToolInput(BaseModel):
    id: int = Field(..., description="El ID del correo electrónico.")
    subject: str = Field(..., description="El asunto del correo electrónico.")
    email_text: str = Field(..., description="El texto completo del correo electrónico.")
    importancia: Literal["alta", "media", "baja"] = Field(..., description="La importancia asignada al correo.")

@tool(args_schema=FeedbackToolInput)
def handle_feedback_tool(id: int, subject: str, email_text: str, importancia: Literal["alta", "media", "baja"]) -> dict:
    """
    Maneja los correos de feedback.
    """
    testimonios_file = "testimonios.txt"
    with open(testimonios_file, "a", encoding="utf-8") as f:
        f.write(f"--- Testimonio de {datetime.now().strftime('%Y-%m-%d')} ---\n")
        f.write(f"Mensaje: {email_text}\n")
    print(f"--- Acción: Feedback ---")
    print(f"Testimonio del ID {id} guardado en '{testimonios_file}'.")
    return {"clasificacion": "Feedback", "importancia": importancia, "mensaje": None}

# Todas las herramientas disponibles para el LLM
tools = [handle_cita_tool, handle_precios_tool, handle_reclamo_tool, handle_feedback_tool]

# --- 3. Nodo del Grafo que Llama y Ejecuta la Herramienta ---

def check_email_age_and_update_importance(state: EmailClassificationState) -> EmailClassificationState:
    """
    Compara la fecha del correo con la actual y aumenta la importancia si han pasado más de 2 días.
    """
    try:
        # Asegúrate de que el formato de la fecha sea 'YYYY-MM-DD'
        email_date = datetime.strptime(state['date'], '%Y-%m-%d')
        today = datetime.now()
        age_in_days = (today - email_date).days
        
        # Aumenta la importancia si el correo tiene más de 2 días
        if age_in_days > 2:
            current_importance = state['importancia']
            if current_importance == 'baja':
                state['importancia'] = 'media'
                print(f"INFO: Correo con ID {state['id']} es viejo ({age_in_days} días). Importancia actualizada a 'media'.")
            elif current_importance == 'media':
                state['importancia'] = 'alta'
                print(f"INFO: Correo con ID {state['id']} es muy viejo ({age_in_days} días). Importancia actualizada a 'alta'.")
                
    except (ValueError, KeyError) as e:
        print(f"ADVERTENCIA: No se pudo verificar la fecha del correo para el ID {state['id']}. Error: {e}")
        # El estado no se modifica si hay un error en la fecha
        
    return state


async def call_tool_node(state: EmailClassificationState) -> EmailClassificationState:
    """
    Este nodo utiliza el LLM para seleccionar y llamar a una de las herramientas de acción,
    y luego ajusta la importancia según la antigüedad del correo.
    """
    llm_with_tools = llm.bind_tools(tools)
    prompt_with_tools = PromptTemplate(
        template="""Eres un asistente de clasificación de emails para un spa. Tu tarea es analizar el correo proporcionado y, basándote en su contenido, seleccionar una de las siguientes herramientas para procesarlo. Es **obligatorio** que siempre selecciones una herramienta.

        Instrucciones:
        1. **Clasifica el correo**: ¿Es una "Solicitud de cita", "Consulta de precios/promociones", "Reclamo", o "Feedback"?
        2. **Asigna importancia**: 'alta' (para reclamos), 'media' (para solicitudes de cita), o 'baja' (para otros).
        3. **Selecciona la herramienta**: Elige la función de herramienta que coincida con la clasificación y pásale los argumentos correctos.
        4. **No modifiques el asunto aquí**: Si es un reclamo, la herramienta se encargará de ajustar el asunto del correo.
        Fecha del correo: {date}
        Asunto: "{subject}"
        Correo: "{email_text}"
        """,
        input_variables=["subject", "email_text", "date"],
    )
    llm_input = {
        "subject": state['subject'],
        "email_text": state['email_text'],
        "date": state['date']
    }
    ai_message = await llm_with_tools.ainvoke(prompt_with_tools.format(**llm_input))

    if ai_message.tool_calls:
        tool_call = ai_message.tool_calls[0]
        tool_name = tool_call['name']
        tool_args = tool_call['args']
        
        # Lógica para modificar el asunto si es un reclamo (esta sección ahora está vacía)
        if tool_name == 'handle_reclamo_tool':
            # Se asegura de que la fecha original se pase a la herramienta
            tool_args['date'] = state['date']


        chosen_tool = next((t for t in tools if t.name == tool_name), None)
        if not chosen_tool:
            raise ToolException(f"Herramienta '{tool_name}' no encontrada.")
        
        result = await chosen_tool.ainvoke(tool_args)
        
        state['clasificacion'] = result.get("clasificacion")
        state['importancia'] = result.get("importancia")
        state['tool_name'] = tool_name
        state['mensaje'] = result.get("mensaje")

        # Llama a la función para verificar la antigüedad y actualizar la importancia
        state = check_email_age_and_update_importance(state)

    else:
        raise ValueError("El modelo de lenguaje no pudo seleccionar una herramienta adecuada para el correo.")
        
    return state

# --- 4. Construcción y Compilación del Grafo ---

def build_graph():
    """Crea y compila el grafo de LangGraph."""
    workflow = StateGraph(EmailClassificationState)
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
    date: str
    subject: str
    email_text: str

# Definimos el modelo de Pydantic para la respuesta
class ClassificationResponse(BaseModel):
    id: int
    subject: str
    email_text: str
    date: datetime
    clasificacion: Literal["Solicitud de cita", "Consulta de precios/promociones", "Reclamo", "Feedback"] = Field(
        ...,
        description="La clasificación del correo electrónico."
    )
    importancia: Literal["alta", "media", "baja"] = Field(
        ...,
        description="La importancia del correo electrónico."
    )
    mensaje: Optional[str] = Field(
        None,
        description="Mensaje adicional, como la lista de precios, en el caso de consultas."
    )

@app.post("/classify-email", response_model=ClassificationResponse)
async def classify_email_endpoint(email_request: EmailRequest):
    """
    Recibe un solo correo electrónico, lo clasifica y detona una acción.
    """
    try:
        initial_state = {
            'id': email_request.id,
            'subject': email_request.subject,
            'email_text': email_request.email_text,
            'date': email_request.date,
            'clasificacion': '',
            'importancia': '',
            'tool_name': '',
            'mensaje': None
        }
        
        final_state = await email_classifier_graph.ainvoke(initial_state)
        
        return ClassificationResponse(
            id=final_state['id'],
            subject=final_state['subject'],
            email_text=final_state['email_text'],
            date=final_state['date'],
            clasificacion=final_state['clasificacion'],
            importancia=final_state['importancia'],
            mensaje=final_state.get('mensaje')
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/download-testimonios")
async def download_testimonios():
    """
    Endpoint para descargar el archivo de testimonios.txt.
    """
    file_path = "testimonios.txt"
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="text/plain", filename="testimonios.txt")
    else:
        raise HTTPException(status_code=404, detail="El archivo testimonios.txt no se encontró.")
