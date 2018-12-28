from flask import Flask, render_template, request, flash, redirect, url_for, session
from flask_mail import Mail, Message
import os
from dbUtils import register as registrarDB #Obtenemos el archivo register desde dbUtils
from dbUtils import tokens as tokenDB #Obtenemos el archivo tonke ns desde dbUtils
from flask import jsonify

mailServer = Mail() #Creamos un servidor de Email
app = Flask(__name__) #Creamos la app de flask
app.config.update(dict(                     #
    DEBUG = True,                           #
    MAIL_SERVER = 'smtp.gmail.com',         #
    MAIL_PORT = 587,                        # Configuramos la smtp gratis de gmail
    MAIL_USE_TLS = True,                    #   
    MAIL_USE_SSL = False,                   #
    MAIL_USERNAME = 'Email',                #
    MAIL_PASSWORD = 'Contraseña',           #
))
mailServer.init_app(app) #Iniciamos el servidor de correos
app.secret_key = os.urandom(32) #Ponemos la secret key encriptar las sessions y cookies
@app.route('/', methods=["GET", "POST"]) #Configuramos la ruta de indice
def index():
    if request.method == "POST": #Si el usuario apreta el boton del formulario
        session['mail'] = request.form.get('email') #Obtenemos el valor del campo con nombre emal
        #TODO: comparacion de contraseñas
        return redirect(url_for('login')) #Redireccionamos al metodo login que esta mas abajo
    
    return render_template('index.html') #Cuando el metodo sea GET renderizamos la template index.html

@app.route('/register', methods=["GET", "POST"]) #Configuramos la ruta register
def register(): 
    if request.method == "POST": #Si se presiona el boton del formulario
        mail = request.form.get('email') #Se obtiene el valor del campo con nombre email
        password = request.form.get('pass') #Se obtiene el valor del campo con nombre pass
        confirm_pass = request.form.get('pass2') # Se obtiene el valor del campo pass2
        if not password == confirm_pass: # Si las contraseñas no coinciden
            password_error = 'Las contaseñas no coinciden' #Creamos un mensaje que diga las contraseñas no coinciden
            flash(password_error) #Mandamos el mensaje al HTML con el metodo "flash"
        else: #Si las contraseñas coinciden
           user_id = registrarDB.registrar_usuario(mail, password) # Registramos el usuario con la funcion registrar usuario 
           if not user_id: #Si el usuario ya existe
               user_exist = "El usuario ya existe"  #
               flash(user_exist)                    #Enviamos un mensaje al HTML con el metodo "flash"
           else: #Si el usuario no existe
            token = tokenDB.createToken(user_id) #Creamos el token en la base de datos
            link = "http://127.0.0.1:5000/confirm_step/{}".format(token) #Formateamos la string con el token
            #Creamos el mensaje de confirmacion
            msg = Message("Confirma tu mail", sender='jcrispis56@gmail.com', recipients=[mail], body="Hola {} te damos la bienvenida a la pagina para confirmar sigue este link: \n\n{} \n\n este link tiene una duracion de 30 minutos".format(mail, link))
            mailServer.send(msg) #Enviamos el mail
            session['register'] = True #Creamos una cookie para decir que el usuario esta registrado
            return redirect(url_for('confirm')) #Redireccionamos a la pagina de confirmacion 
    return render_template('register.html') # Si el metodo es get retornamos la template

@app.route('/confirm', methods=["GET"]) #Configuramos la ruta
def confirm(): 
    if "register" in session: #Comprobamos si el usuario termino el registro
        session.pop('register', None) #Quitamos la cookie de registro
        return render_template('confirm.html') #Devolvemos el template de confirm
    else:
        return "Algo ha salido mal :(" #Si no devolvemos un error
@app.route('/confirm_step/<RegID>') #Configuramos la ruta de confirmacion y como variable leemos el token
def confirm_step(RegID): #Hacemos la funcion que se ejecuta al acceder a la ruta reciviendo como parametro el token
    RegID = str(RegID)
    confirmacion = tokenDB.getTokenAndConfirm(RegID) #Llamamos a la funcion de tokens.py para confirmar el usuario
    if not confirmacion: #Si la funcion devuelve nulo o false
        return "Hubo un error en procesar los datos vuelva a intentarlo" #Devolvemos una string al navegador
    else: # Si la funcion devuelve True
        session['Redirected'] = True #Ponemos la cookie de redirected
        return redirect(url_for('gracias')) #Y redireccionamos a la pagina de agradecimiento
    return " " #No retornamos nada
 
@app.route('/gracias')
def gracias():
    if 'Redirected' in session: #Si la cookie "Redirected" esta presente
        session.pop("Redirected", None) #Quitamos la cookie
        return render_template('gracias.html') #Enviamos el html al navegador
    else: #Si npo esta la cookie
        return "Algo ha salido mal :(" #Enviamos una string al navegador

@app.route('/login') #Configuramos la ruta login
def login():
    if 'mail' in session: #Si la sesion contiene un mail
        mail = session.get('mail') #Obtenemos el email de las cookies
        mongoResp = registrarDB.return_confirmed(mail) #Comprobamos si esta confirmado
        if mongoResp[0] == True: #Si esta confirmado
            return "bienvenido: "+mail #Le damos una bienvenida
            #TODO: Pagina de incio de usuario
        elif mongoResp[0] == False: #Si la respuesta de mongo es falsa
            session.pop('mail', None) # Quitamos el mail de las cookies
            session['register'] = True # Ponemos la cooke para mostrar la pagina para confirmar mail
            return redirect(url_for('confirm'))
        elif mongoResp[0] == 3: #Si el usuario no esta registrado
            session.pop('mail', None) #Quitamos el mail de las cookies
            #TODO: Autorellenado de formulario
            return redirect(url_for('register')) #Y lo redireccionamos a la pagina de registro
    else: #Si no tiene un mail
        return "Algo salio mal :(" #Enviamos un string al navegador

        
    
if __name__ == '__main__': #Si lo ejecutamos desde este archivo
    app.run(debug=True) #Corremos la aplicacion en modo debug
    