from pymongo import MongoClient
from datetime import datetime, timedelta
from uuid import uuid4
import random
import string
from dbUtils.register import confirmar
def connection():
    
    client = MongoClient() #Creamos el cliente mongoDB
    db = client['red_social'] #Conectamos a la database
    tabla = db['sessions_tokens'] #Conectamos a la coleccion de sessions tokens
    return tabla #Retornamos la tabla

def createToken(ID):
    tabla = connection() # Obtenemos la coleccion
    token_cript = uuid4().hex # Creamos un token uuid y lo retornamos en hexadecimal
    token = {} #creamos diccionario de tokens
    token["id_user"] = ID #Asociamos la ID de usuarios
    token["fecha_creacion"] = datetime.now().timestamp() #Creamos un timestamp de la hora en este momento
    token["fecha_vencimiento"] = (datetime.now() + timedelta(minutes=30)).timestamp() #Creamos otro que tenga la hora dentro de 30 minutos
    token['token'] = token_cript #Asociamos el token
    tabla.insert_one(token) #Ingresamos los datos en la base de datos
    return token_cript #Retornamos el token para hacer el link

def getTokenAndConfirm(token):
    tabla = connection() #Conectamos a la taba
    var = tabla.find_one({'token':token}) #Encontramos el token
    fecha = var['fecha_creacion'] #Obtenemos la fecha de creacion
    fecha_utc = datetime.utcfromtimestamp(fecha) # La pasamos a UTC
    fecha_vencimiento = var['fecha_vencimiento'] # Obtenemos la fecha de vencimiento
    fecha_vencimiento_utc = datetime.utcfromtimestamp(fecha_vencimiento) # La pasamos a utc
    if not var: #Si el valor no existe
        return False #Retornamos False
    else: #Si existe
        if fecha_utc > fecha_vencimiento_utc: #Comparamos las fechas para ver si el token no esta vencido
            return False #Si esta vencido retornamos un False
        else: #Si no esta vencido
            confirmar(var["id_user"]) # Cambiamos el valor de confirm del usario desde la otra tabla
            tabla.delete_one({'token':token}) #Borramos el token
            return True #Retornamos Verdadero


    