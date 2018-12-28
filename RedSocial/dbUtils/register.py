from pymongo import MongoClient
from bson import ObjectId
from bson.json_util import dumps
from datetime import datetime
import json
def connection():
    client = MongoClient() #Creamos el cliente de mongo
    db = client['red_social'] #Entramos a la db Red_social
    tabla = db['users'] #Entramos a la tabla de usuarios
    return tabla #Devolvemos la tabla


def registrar_usuario(mail, contraseña):
    tabla = connection() #Obtenemos la tabla de usuarios
     
    existente = tabla.find_one({'mail':mail}) #Buscamos si el mail esta registrado
    if existente: #Si el valor no es None
        return None #Retornamos None para parsearlo en el archivo app.py
    new_user = {} #Si no creamos un diccionario para el usuario
    new_user['date'] = datetime.now().timestamp() #Obtenemos la hora del registro
    new_user['mail'] = mail #Guardamos el mail
    #TODO: Encriptar contraseñas
    new_user['contraseña'] = contraseña #Guardamos la contraseña
    new_user['confirm'] = False #Guardamos la confirmacion por correo como falsa porque no se ha hecho
    user_id = tabla.insert(new_user) #Insertamos el usuario y guardamos su ID
    return user_id #Retornamos la ID para usarla despues

def confirmar(ID):
    tabla = connection() #Obtenemos la tabla
    id_modify = {"_id":ObjectId(ID)} #Ponemos la id de usuario para hacer la busqueda
    new_value = {'$set':{"confirm":True}} #Ponemos el nuevo valor que seria confirmado
    count = tabla.update_one(id_modify, new_value) #Actualizamos los valores de confirmacion
    if count > 0: #Si se modificaron valores
        return True #Retornamos que se modificaron los valores de la tabla
    else:
        return False #Retornamos que no se encontraron dichos valores
#Funciones para testear
def delete(ID):
    tabla = connection() #Obtenemos la tabla 
    tabla.delete_one({'_id':ObjectId(ID)}) #Borramos una ID
    print('Borrado') #Mandamos un mensaje por consola
#Funciones para testear
def find_all():
    tabla = connection() #Obtenemos la tabla
    vals = tabla.find() #Encontramos los valores
    return dumps(vals) #Los pasamos de bson a texto
#Funciones para testear
def find_one(ID):
    tabla = connection() #Obtenemos la tabla
    var = tabla.find_one({'_id':ObjectId(ID)}) #Encontramos el valor con dicha ID
    return dumps(var) #Pasamos de BSON a texto
#Funciones para testear
def delete_all():
    var = json.loads(find_all()) #Pasamos de texto a JSON
    for i in var: #Iteramos el JSON
        ID = i['_id']['$oid'] #Obtenemos la ID para borrar
        delete(ID) #Borramos el valor

def return_confirmed(correo):
    tabla = connection() #Obtenemos la tabla
    var = tabla.find_one({'mail':correo}) #Buscamos el valor con ese correo 
    try:
        if var["confirm"] == True: #Intentamos buscar el valor
            return (True, str(var["_id"]), var["mail"]) #Retornamos que el usuario esta confirmado
        elif var["confirm"] == False:
            return (False, 0, 0) #Retornamos que esta registrado pero no confirmado
    except:
        return (3,0,0) #Retornamos que no esta registrado
if __name__ == '__main__': #Si se ejecuta desde este archivo
    delete_all() #
    find_all()   #
    
