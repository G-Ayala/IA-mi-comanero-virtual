# Importamos Flask y sus utilidades
# Importamos render_template para renderizar archivos HTML
# Importamos request para recibir datos del frontend
# Importamos jsonify para convertir datos Python a formato JSON y enviarlos al frontend
from flask import Flask, render_template, request, jsonify
# Importamos la librería de Gemini AI
import google.generativeai as genai
# Importamos PIL para manejar imágenes
from PIL import Image
# Importamos io para manejar archivos en memoria (sin guardar en disco)
import io
# Importamos os para leer variables de entorno
import os
# Importamos base64 para decodificar imágenes del frontend
import base64

# Creamos una instancia de la aplicación Flask
# __name__ le dice a Flask el nombre del módulo actual
app = Flask(__name__)

# Configuramos la API key de Gemini desde variable de entorno
# Esto es más seguro que hardcodear la key en el código
# La variable se define en .env o en la configuración de Render
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

# Creamos una instancia del modelo Gemini
# Este modelo puede analizar tanto texto como imágenes
model = genai.GenerativeModel('gemini-2.5-flash')   #gemini-1.5-flash///gemini-2.5-flash///gemini-2.0-flash-exp


def analizar_imagen(imagen_bytes):
    #imagen_bytes: Los bytes de la imagen en formato binario
    # Convertimos los bytes a un objeto Image de PIL
    # io.BytesIO crea un objeto tipo archivo en memoria
    img = Image.open(io.BytesIO(imagen_bytes))
    
    # Llamamos a Gemini para generar la descripción
    # Le pasamos el prompt y la imagen
    response = model.generate_content([
        "Describe detalladamente lo que ves en esta imagen en español, usando texto plano sin usar caracteres especiales y de manera clara para que pueda ser leído en voz alta",
        img
    ])
    
    # Retornamos solo el texto de la respuesta de gemini
    return response.text


# Ruta principal - muestra la interfaz web
# Definimos una ruta (endpoint) para la página principal
# @ es un decorador que modifica el comportamiento de la función
# @app.route('/') significa que esta función se ejecuta cuando alguien visita la raíz del sitio (ej: ejemplo.com/)
@app.route('/')
def index():
    # render_template busca el archivo index.html en la carpeta 'templates/'
    # y lo envía como respuesta al navegador del usuario
    return render_template('index.html')


# Definimos otra ruta para procesar datos
# methods=['POST'] significa que esta ruta SOLO acepta peticiones POST (no GET)
# Las peticiones POST se usan para enviar datos al servidor
@app.route('/analizar', methods=['POST'])
def analizar():
    """
    Recibe una imagen desde el frontend, la analiza y devuelve la descripción
    
    Expected JSON:
        {
            "image": "data:image/jpeg;base64,/9j/4AAQ..." 
        }
    
    Returns:
        JSON: {"descripcion": "texto generado por Gemini"}
    """
    try:
        # request.json obtiene los datos JSON enviados desde el frontend
        # Por ejemplo, si el frontend envía: {"input": "hola"}
        # entonces data será un diccionario: {'input': 'hola'}
        data = request.json
        
        # Extraemos la imagen en formato base64
        # El frontend envía: "data:image/jpeg;base64,XXXXX"
        image_data = data['image']
        
        # Removemos el prefijo "data:image/jpeg;base64," para obtener solo el base64
        # split(',')[1] toma la segunda parte después de la coma
        image_base64 = image_data.split(',')[1]
        
        # Decodificamos el string base64 a bytes
        # base64.b64decode convierte el texto base64 a datos binarios
        image_bytes = base64.b64decode(image_base64)
        
        # Llamamos a nuestra función para analizar la imagen
        descripcion = analizar_imagen(image_bytes)
        
        # Devolvemos la descripción en formato JSON
        # jsonify convierte un diccionario Python a formato JSON
        # Creamos un diccionario con el resultado: {'resultado': valor}
        # El frontend puede entonces leer data.resultado en JavaScript
        return jsonify({
            'descripcion': descripcion,
            'status': 'success'
        })
    
    except Exception as e:
        # Si hay algún error, lo capturamos y devolvemos un mensaje
        # str(e) convierte el error a string
        print(f"Error: {str(e)}")  # Log del error en consola
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500  # Código HTTP 500 = Error del servidor


# Inicia el servidor en modo desarrollo
if __name__ == '__main__':
    # debug=True solo para desarrollo local
    # host='0.0.0.0' permite acceso desde otras máquinas en tu red
    # port=5000 es el puerto por defecto
    app.run(debug=True, host='0.0.0.0', port=5000)