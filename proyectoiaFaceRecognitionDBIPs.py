import cv2

import mediapipe as mp

import numpy as np

import requests

import mysql.connector
import pandas as pd

import time
import socket
from mysql.connector import Error

# Función para obtener IP pública

def obtener_ip_publica():

    try:

        respuesta = requests.get('https://api.ipify.org?format=json')

        respuesta.raise_for_status()  # Lanza un error si la solicitud no fue exitosa

        ip_publica = respuesta.json()['ip']

        return ip_publica

    except requests.RequestException as e:

        return f"Error al obtener la IP pública: {e}"
#Obtener ip privada
def obtener_ip_privada():

    hostname = socket.gethostname()

    ip_privada = socket.gethostbyname(hostname)

    return ip_privada


#Funcion para Data frame

# Función para insertar datos en MySQL

def insertar_datos(ip_publica, ip_privada, nombre_usuario):

    conexion = mysql.connector.connect(

        host='195.179.238.58',  # Cambia por la dirección de tu servidor MySQL

        database='u927419088_testing_sql',  # Cambia por el nombre de tu base de datos

        user='u927419088_admin',  # Cambia por tu usuario de MySQL

        password='#Admin12345#'  # Cambia por tu contraseña de MySQL

    )


    cursor = conexion.cursor()


    query = "INSERT INTO datos_usuario (ip_publica, ip_privada, nombre_usuario) VALUES (%s, %s,%s)"

    valores = (ip_publica, ip_privada, nombre_usuario)


    cursor.execute(query, valores)




    conexion.commit()



    cursor.close()

    conexion.close()


#Insertar ip privada
#este segmento de codigo se quito para utilizar con la funcion insertar_datos anterior tambien
#guardar tanto la ip publica ip privada y el nombre de uusario



#-------------------------------------------------------------


#-------------------------------------------------------------




# Inicializar Mediapipe FaceMesh

mp_face_mesh = mp.solutions.face_mesh

face_mesh = mp_face_mesh.FaceMesh(min_detection_confidence=0.5, min_tracking_confidence=0.5)


mp_drawing = mp.solutions.drawing_utils

drawing_spec = mp_drawing.DrawingSpec(thickness=1, circle_radius=1)


cap = cv2.VideoCapture(0)


def calcular_distancia(punto1, punto2):

    return np.linalg.norm(np.array(punto1) - np.array(punto2))


# Obtiene la IP pública

ip_publica = obtener_ip_publica()

#Obtiene la IP privada
ip_privada=obtener_ip_privada()


# Nombre del usuario

nombre_usuario = "Marco"


boca_abierta = False

inicio_boca_abierta = 0

umbral_duracion = 2  # Segundos que la boca debe estar abierta para enviar datos


while cap.isOpened():

    success, frame = cap.read()

    if not success:

        print("No se puede acceder a la cámara")

        break


    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    image.flags.writeable = False


    results = face_mesh.process(image)


    image.flags.writeable = True

    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)


    if results.multi_face_landmarks:

        for face_landmarks in results.multi_face_landmarks:

            mp_drawing.draw_landmarks(

                image=image,

                landmark_list=face_landmarks,

                connections=mp_face_mesh.FACEMESH_TESSELATION,

                landmark_drawing_spec=drawing_spec,

                connection_drawing_spec=drawing_spec)


            labio_superior = face_landmarks.landmark[13]

            labio_inferior = face_landmarks.landmark[14]


            altura, ancho, _ = image.shape

            labio_superior = (int(labio_superior.x * ancho), int(labio_superior.y * altura))

            labio_inferior = (int(labio_inferior.x * ancho), int(labio_inferior.y * altura))


            distancia_boca = calcular_distancia(labio_superior, labio_inferior)


            umbral_boca_abierta = 10


            if distancia_boca > umbral_boca_abierta:

                if not boca_abierta:

                    boca_abierta = True

                    inicio_boca_abierta = time.time()

                elif time.time() - inicio_boca_abierta > umbral_duracion:

                    cv2.putText(image, '¡Boca Abierta!', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2,

                                cv2.LINE_AA)


                    # Enviar datos a la base de datos

                    insertar_datos(ip_publica, ip_privada,nombre_usuario)
                   # insertar_datosp(ip_privada, nombre_usuario)

                    print("Se guardó el registro en la base de datos...")
                # ******************************************************
                # Seleccion de registro para leer y grabar en excel
                    # &&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
                    # Ejecutar consulta SELECT
                    conexion = mysql.connector.connect(

                        host='195.179.238.58',  # Cambia por la dirección de tu servidor MySQL

                        database='u927419088_testing_sql',  # Cambia por el nombre de tu base de datos

                        user='u927419088_admin',  # Cambia por tu usuario de MySQL

                        password='#Admin12345#'  # Cambia por tu contraseña de MySQL

                    )

                    cursor = conexion.cursor()
                    query = 'SELECT * FROM datos_usuario'
                    df = pd.read_sql(query, conexion)

                    if df.empty:
                        print("No se encontraron datos en la base de datos.")
                    else:
                        print(df)

                        try:
                            # Exportar a CSV
                            df.to_csv('datos_usuario.csv', index=False)
                            print('Datos exportados a CSV con éxito')

                            # Exportar a Excel
                            df.to_excel('datos_usuario.xlsx', index=False, engine='openpyxl')
                            print('Datos exportados a Excel con éxito')

                        except Exception as e:
                            print(f"Error al exportar los datos: {e}")
                        finally:
                            if conexion.is_connected():
                                cursor.close()
                                conexion.close()

                    # &&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
                   # query_to_dataframe()



                #******************************************************

                    inicio_boca_abierta = time.time()  # Reiniciar el temporizador para enviar nuevamente si se mantiene abierta

            else:

                boca_abierta = False  # Resetear si la boca se cierra


    cv2.imshow('Reconocimiento de Gestos Faciales', image)


    if cv2.waitKey(5) & 0xFF == ord('q'):

        break


cap.release()

cv2.destroyAllWindows()

#query_to_dataframe()