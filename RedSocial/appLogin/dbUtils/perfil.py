from pymongo import MongoClient
from bson.json_util import dumps
import os
import shutil
def connection():
    client = MongoClient()
    db = client['red_social']
    return db['perfil']

def perfilFind(mail):
    query = {}
    query['mail'] = mail
    tabla = connection()
    return tabla.find_one(query)

def ingresarNuevo(Mail, image_url = None, nickname='', biography=''):
    get_query = perfilFind(Mail)
    tabla = connection()
    if get_query:
        object_modify = {'mail':Mail}
        print(image_url)
        if not image_url == None:
            file = os.path.abspath("./"+get_query['image_url'])
            os.remove(file)
            query_modify = {'$set':{'image_url':image_url}}
            tabla.update_one(object_modify, query_modify)
        if not nickname == '':
            query_modify = {'$set':{'nickname':nickname}}
            tabla.update_one(object_modify, query_modify)
        if not biography == '':
            query_modify = {'$set':{'biography':biography}}
            tabla.update_one(object_modify, query_modify)
        else:
            pass
    else:
        query = {}
        query['mail'] = Mail
        query['nickname'] = ''
        if not image_url:
            query['image_url'] = ''
        else:
            query['image_url'] = image_url
        query['biography'] = ''
        query['friends'] = []
        query['likes'] = 0
        query['publications'] = []
        tabla.insert_one(query)




def perfilFindAll():
    print(dumps(connection().find()))
def deleteAll():
    finds = connection().find()
    for i in finds:
        connection().delete_one(i)

if __name__ == "__main__":
    perfilFindAll()
