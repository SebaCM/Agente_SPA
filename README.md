# Agente_SPA
Pipeline de Clasificación de Emails para Spa Bella LunaEste proyecto implementa un pipeline de clasificación y enrutamiento de correos electrónicos utilizando un modelo de lenguaje grande (LLM) y la API de FastAPI. El objetivo es procesar automáticamente los correos de clientes del "Spa Bella Luna", clasificarlos por intención, asignarles una prioridad y detonar una acción específica para cada tipo de correo.Tecnologías UtilizadasLenguaje: Python 3.8+LLM: Gemini-Pro (a través de la API de Google)Framework Web: FastAPILibrería de LLM: LangChain, LangGraphContenedores (Opcional): DockerServicio de Email (Opcional): Gmail (vía smtplib)RequisitosPara ejecutar el proyecto, necesitarás:Python 3.8 o superior instalado.Una clave de API de Google para acceder a Gemini.Credenciales de Gmail (usuario y clave de aplicación) si deseas probar la funcionalidad de envío de correos de reclamo.Docker (opcional, para la sección Plus).Instalación y ConfiguraciónSigue estos pasos para poner en marcha el proyecto:Clonar el repositorio:git clone https://github.com/tu-usuario/nombre-del-repositorio.git
cd nombre-del-repositorio
Crear y activar un entorno virtual:python3 -m venv venv
source venv/bin/activate
Instalar las dependencias:pip install -r requirements.txt
Configurar las variables de entorno:Crea un archivo .env en la raíz del proyecto con tus claves y credenciales.Nota: Si usas autenticación de dos factores en Gmail, necesitarás generar una clave de aplicación para usar como contraseña.
GOOGLE_API_KEY=""
GMAIL_USER="correo_gmail@gmail.com"
GMAIL_PASS=""
Uso de la APIIniciar el servidor de FastAPIEjecuta el siguiente comando para iniciar el servidor web:uvicorn main:app --reload
Una vez que el servidor esté activo, puedes acceder a la documentación interactiva (Swagger UI) en http://127.0.0.1:8000/docs.Probar el endpoint de clasificaciónPuedes enviar una solicitud POST al endpoint /classify-email con un JSON que contenga los detalles del correo.Ejemplo de solicitud:curl -X POST "http://127.0.0.1:8000/classify-email" \
-H "Content-Type: application/json" \
-d '{
  "id": 1,
  "subject": "Reserva tratamiento corporal",
  "email_text": "¿Tienen disponibilidad para un masaje relajante el viernes por la tarde?"
}'
Dockerización (Plus)Si tienes Docker instalado, puedes desplegar la API en un contenedor.1. Construir la imagen de Dockerdocker build -t spa-ai-api .
2. Ejecutar el contenedordocker run -d --name spa-api-container -p 8000:8000 spa-ai-api
Esto expondrá el puerto 8000 del contenedor al puerto 8000 de tu máquina local.Criterios de Evaluación y LógicaEl pipeline utiliza la siguiente lógica para clasificar y asignar prioridad:Clasificación: El LLM clasifica el correo en una de las cuatro categorías: Solicitud de cita, Consulta de precios/promociones, Reclamo, o Feedback.Prioridad:Alta: para correos clasificados como Reclamo.Media: para correos clasificados como Solicitud de cita.Baja: para cualquier otra clasificación.
