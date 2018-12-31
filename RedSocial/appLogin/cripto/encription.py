import hashlib

def encryptPass(password):
    md5 = hashlib.md5(password.encode()).hexdigest()  #Creamos un hash md5 para almacenar el passwored
    myHash = hashlib.sha256(md5.encode()).hexdigest() #Lo pasamos a Sha-256
    return myHash.upper() #Lo ponemos en mayusculas

def decriptPass(password, password_enc):
    encoded = encryptPass(password) #Encriptamos el password
    if encoded == password_enc: #Lo comparamos con el de la base de datos
        return True #Retornamos True si las contraseñas coinciden
    else:
        return False #Retornamos False si las contraseñas no coinciden
