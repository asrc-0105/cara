# Importamos las bibliotecas necesarias para trabajar con la cámara, la detección de emociones y el puerto serial
import cv2  # Para trabajar con la cámara y mostrar el video
from deepface import DeepFace  # Para analizar las emociones en las imágenes
import serial  # Para enviar datos a través de un puerto serial

# Configuramos el puerto serial donde se enviarán los datos
puerto_serial = serial.Serial('COM10', 9600)  # Especificamos el puerto COM y la velocidad en baudios
puerto_serial.close()  # Aseguramos que el puerto esté cerrado inicialmente
puerto_serial.open()  # Abrimos el puerto serial para poder enviar datos más adelante

# Activamos la cámara para capturar el video en tiempo real
captura_video = cv2.VideoCapture(0)  # El número '0' indica la cámara por defecto de la computadora

# Definimos una lista de emociones que queremos detectar en el orden en que deben aparecer
emociones_a_detectar = ['happy', 'sad']  # Emociones que se buscarán: feliz (happy) y triste (sad)

# Inicializamos una variable que nos dirá cuál emoción estamos buscando en un momento dado
indice_emocion_actual = 0  # Comenzamos con la primera emoción en la lista (índice 0)

# Creamos una función para enviar datos al puerto serial basándonos en la emoción detectada
def enviar_datos_segun_emocion(emocion):
    # Esta función enviará un carácter diferente según la emoción detectada
    if emocion == 'happy':
        # Si la emoción detectada es "happy", enviamos una 'H' al puerto serial
        dato_a_enviar = 'H'  # La letra que queremos enviar al puerto
    elif emocion == 'sad':
        # Si la emoción detectada es "sad", enviamos una 'S' al puerto serial
        dato_a_enviar = 'S'  # La letra que queremos enviar al puerto
    else:
        # Si no es una emoción que estamos buscando, no enviamos nada
        dato_a_enviar = ''  # No enviamos ningún dato

    # Solo enviamos el dato si no está vacío
    if dato_a_enviar != '':
        # Convertimos el dato a un formato que pueda ser enviado por el puerto serial
        puerto_serial.write(str.encode(dato_a_enviar))

# Creamos una función para procesar cada fotograma que capturamos del video
def analizar_fotograma(fotograma):
    global indice_emocion_actual  # Usamos la variable global para saber qué emoción estamos buscando
    
    # Utilizamos DeepFace para analizar la emoción en el fotograma que capturamos
    resultados = DeepFace.analyze(fotograma, actions=['emotion'], enforce_detection=False)
    
    # Si detecta múltiples caras, tomamos solo la primera, de lo contrario usamos la única cara
    if isinstance(resultados, list):
        resultado = resultados[0]  # Si hay varias caras, tomamos la primera
    else:
        resultado = resultados  # Si solo hay una cara, usamos ese resultado

    # Extraemos la emoción dominante detectada y la región donde está la cara
    emocion_detectada = resultado['dominant_emotion']  # Sacamos la emoción predominante
    region_cara = resultado['region']  # Obtenemos las coordenadas de la cara en el fotograma

    # Dibujamos el nombre de la emoción detectada sobre el video
    cv2.putText(fotograma, emocion_detectada, (region_cara['x'], region_cara['y'] - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    
    # Dibujamos un rectángulo alrededor de la cara detectada
    cv2.rectangle(fotograma, (region_cara['x'], region_cara['y']), 
                  (region_cara['x'] + region_cara['w'], region_cara['y'] + region_cara['h']),
                  (0, 255, 0), 2)

    # Si la emoción detectada es la que estamos buscando, enviamos los datos
    if emocion_detectada == emociones_a_detectar[indice_emocion_actual]:
        enviar_datos_segun_emocion(emocion_detectada)  # Llamamos a la función que envía la emoción al serial

        # Pasamos a buscar la siguiente emoción en la lista
        indice_emocion_actual += 1
        
        # Si ya hemos detectado todas las emociones de la lista, terminamos el programa
        if indice_emocion_actual >= len(emociones_a_detectar):
            captura_video.release()  # Liberamos la cámara
            cv2.destroyAllWindows()  # Cerramos todas las ventanas de OpenCV
            puerto_serial.close()  # Cerramos el puerto serial
            exit()  # Terminamos el programa

# Bucle principal del programa: captura el video continuamente y procesa cada fotograma
while True:
    # Capturamos un fotograma de la cámara
    ret, fotograma = captura_video.read()
    
    # Si no se puede capturar el fotograma, salimos del bucle
    if not ret: 
        break

    # Procesamos el fotograma capturado
    analizar_fotograma(fotograma)

    # Mostramos el fotograma procesado en una ventana de video
    cv2.imshow('Video', fotograma)

    # Esperamos a que el usuario presione la tecla 'q' para salir del bucle
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Al finalizar el bucle, liberamos la cámara y cerramos las ventanas
captura_video.release()
cv2.destroyAllWindows()
puerto_serial.close()
