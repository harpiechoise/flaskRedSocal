from pymongo import MongoClient
from bson import ObjectId
from bson.json_util import dumps
from datetime import datetime

def connection():
    client = MongoClient()
    db = client['red_social']
    tabla = db['users']
    return tabla

def registrar_usuario(mail, contraseña):
    tabla = connection()
    
    existente = tabla.find_one({'mail':mail})
    if existente:
        print('El mail ya existe')
        return None
    
    new_user = {}
    new_user['date'] = datetime.utcnow()
    new_user['mail'] = mail
    new_user['contraseña'] = contraseña
    new_user['confirm'] = False
    user_id = tabla.insert(new_user) 
    return user_id

def confirmar(ID):
    tabla = connection()
    id_modify = {"_id":ObjectId(ID)}
    new_value = {'$set':{"confirm":True}}
    count = tabla.update_one(id_modify, new_value)
    print(count.modified_count, ' Valores modificados')
    return True
    
def delete(ID):
    tabla = connection()
    tabla.delete_one({'_id':ObjectId(ID)})
    print('Borrado')

def find_all():
    tabla = connection()
    vals = tabla.find()
    print(dumps(vals))
    
def find_one(ID):
    tabla = connection()
    var = tabla.find_one({'_id':ObjectId(ID)})
    return dumps(var)

def return_confirmed(correo):
    tabla = connection()
    var = tabla.find_one({'mail':correo})
    try:
        if var["confirm"] == True:
            return (True, str(var["_id"]), var["mail"])
        elif var["confirm"] == False:
            return (False, 0, 0)
    except:
        return (3,0,0)
if __name__ == '__main__':
    find_all()
    
