# **Pipeline de Clasificación de Emails para Spa Bella Luna**

Este proyecto implementa un pipeline de clasificación y enrutamiento de correos electrónicos utilizando un modelo de lenguaje grande (LLM) y la API de FastAPI. El objetivo es procesar automáticamente los correos de clientes del "Spa Bella Luna", clasificarlos por intención, asignarles una prioridad y detonar una acción específica para cada tipo de correo.

### **Tecnologías Utilizadas**

* **Lenguaje:** Python 3.8+  
* **LLM:** Gemini-Pro (a través de la API de Google)  
* **Framework Web:** FastAPI  
* **Librería de LLM:** LangChain, LangGraph  
* **Contenedores (Opcional):** Docker  
* **Servicio de Email (Opcional):** Gmail (vía smtplib)

### **Requisitos**

Para ejecutar el proyecto, necesitarás:

* Python 3.8 o superior instalado.  
* Una clave de API de Google para acceder a Gemini.  
* Credenciales de Gmail (usuario y clave de aplicación) si deseas probar la funcionalidad de envío de correos de reclamo.  
* Docker (opcional, para la sección Plus).

### **Instalación y Configuración**

Sigue estos pasos para poner en marcha el proyecto:

1. **Clonar el repositorio:**  
   git clone https://github.com/tu-usuario/nombre-del-repositorio.git  
   cd nombre-del-repositorio

2. **Crear y activar un entorno virtual:**  
   python3 \-m venv venv  
   source venv/bin/activate

3. **Instalar las dependencias:**  
   pip install \-r requirements.txt

4. Configurar las variables de entorno:  
   Crea un archivo .env en la raíz del proyecto con tus claves y credenciales.  
   Necesitarás generar una clave de aplicación para usar como contraseña.  
   GOOGLE\_API\_KEY="tu\_clave\_de\_google\_aqui"  
   GMAIL\_USER="tu\_correo\_gmail@gmail.com"  
   GMAIL\_PASS="tu\_clave\_de\_aplicacion\_aqui"

### **Uso de la API**

#### **Iniciar el servidor de FastAPI**

Ejecuta el siguiente comando para iniciar el servidor web:

uvicorn main:app \--reload

Una vez que el servidor esté activo, puedes acceder a la documentación interactiva (Swagger UI) en http://127.0.0.1:8000/docs.

#### **Probar el endpoint de clasificación**

Puedes enviar una solicitud POST al endpoint /classify-email con un JSON que contenga los detalles del correo.

**Ejemplo de solicitud:**

curl \-X POST "http://127.0.0.1:8000/classify-email" \\  
\-H "Content-Type: application/json" \\  
\-d '{  
  "id": 1,  
  "subject": "Reserva tratamiento corporal",  
  "email\_text": "¿Tienen disponibilidad para un masaje relajante el viernes por la tarde?"  
}'

### **Dockerización (Plus)**

Si tienes Docker instalado, puedes desplegar la API en un contenedor.

#### **1\. Construir la imagen de Docker**

docker build \-t spa-ai-api .

#### **2\. Ejecutar el contenedor**

docker run \-d \--name spa-api-container \-p 8000:8000 spa-ai-api

Esto expondrá el puerto 8000 del contenedor al puerto 8000 de tu máquina local.

### **Criterios de Evaluación y Lógica**

El pipeline utiliza la siguiente lógica para clasificar y asignar prioridad:

* **Clasificación:** El LLM clasifica el correo en una de las cuatro categorías: Solicitud de cita, Consulta de precios/promociones, Reclamo, o Feedback.  
* **Prioridad:**  
  * **Alta:** para correos clasificados como Reclamo.  
  * **Media:** para correos clasificados como Solicitud de cita.  
  * **Baja:** para cualquier otra clasificación.