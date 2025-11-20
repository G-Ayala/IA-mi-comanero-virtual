# Flask para la conexion con html, render_template para renderizar archivos ,request para recibir datos, jsonify para convertir datos JSON y enviarlos al frontend
from flask import Flask, render_template, request, jsonify
# Gemini AI
import google.generativeai as genai
# PIL para manejar im<genes
from PIL import Image
# io para manejar archivos sin guardar
import io
# os para leer variables de entorno
import os
# base64 para decodificar imagenes
import base64

# Instancia de la aplicacion Flask
# __name__ le dice a Flask el nombre del modulo actual
app = Flask(__name__)

# API key de Gemini como variable de entorno
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

# Instancia del modelo Gemini
model = genai.GenerativeModel('gemini-2.5-flash')


def analizar_imagen(imagen_bytes):  #imagen_bytes: bytes de la imagen tomada en el html
    # Convertimos los bytes a un objeto Image y io.BytesIO crea un objeto para trabajar en la memoria
    img = Image.open(io.BytesIO(imagen_bytes))
    
    # Llamada a Gemini para generar la descripción
    response = model.generate_content([
        "Describe detalladamente lo que ves en esta imagen en español, usando texto plano sin usar caracteres especiales y de manera clara para que pueda ser leído en voz alta",
        img
    ])
    
    # Retornamos solo el texto de la respuesta de gemini
    return response.text


# Definimos una ruta (endpoint) para la pagina principal
@app.route('/')
def index():
    # render_template busca el archivo index.html en la carpeta 'templates/' para mostrarlo al usuario
    return render_template('index.html')


# Ruta para procesar datos
# methods=['POST'] para enviar datos al servidor
@app.route('/analizar', methods=['POST'])
def analizar():
    try:
        # request.json obtiene los datos JSON enviados desde el frontend
        data = request.json
        
        # Extraemos la imagen en formato base64 "data:image/jpeg;base64,XXXXX"
        image_data = data['image']
        
        # Removemos el prefijo "data:image/jpeg;base64," para obtener solo el base64
        image_base64 = image_data.split(',')[1]
        
        # Decodificamos el string base64 a bytes
        image_bytes = base64.b64decode(image_base64)
        
        # Llamamos a nuestra funcion para analizar la imagen
        descripcion = analizar_imagen(image_bytes)
        
        # Devolvemos la descripcion en formato JSON creando un diccionario con el resultado: {'resultado': valor}
        return jsonify({
            'descripcion': descripcion,
            'status': 'success'
        })
    
    except Exception as e:
        # Si hay algún error, lo capturamos y devolvemos un mensaje
        print(f"Error: {str(e)}")  # Log del error en consola
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500  # Código HTTP 500 = Error del servidor


# Inicia el servidor en modo desarrollo
if __name__ == '__main__':
    # debug=True solo para desarrollo local
    # host='0.0.0.0' permite acceso desde otras maquinas en la red
    # port=5000 puerto por defecto
    app.run(debug=True, host='0.0.0.0', port=5000)