from flask import Flask, render_template, request, flash, redirect, url_for, session
from flask_mail import Mail, Message
import os
from dbUtils import register as registrarDB #Obtenemos el archivo register desde dbUtils
from dbUtils import tokens as tokenDB #Obtenemos el archivo tonke ns desde dbUtils
from flask import jsonify
from flask import g
from dbUtils import perfil
from werkzeug.utils import secure_filename
mailServer = Mail() #Creamos un servidor de Email
app = Flask(__name__) #Creamos la app de flask
app.config.update(dict(                     #
    DEBUG = True,                           #
    MAIL_SERVER = 'smtp.gmail.com',         #
    MAIL_PORT = 587,                        # Configuramos la smtp gratis de gmail
    MAIL_USE_TLS = True,                    #   
    MAIL_USE_SSL = False,                   #
    MAIL_USERNAME = 'jcrispis56@gmail.com',                #
    MAIL_PASSWORD = 'piamonte121',             #
))

PROFILE_UPLOAD_FOLDER = os.path.abspath('./static/profileImages')
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpge', 'gif'])
app.config["PROFILE_UPLOAD_FOLDER"] = PROFILE_UPLOAD_FOLDER


mailServer.init_app(app) #Iniciamos el servidor de correos
app.secret_key = os.urandom(32) #Ponemos la secret key encriptar las sessions y cookies
def allowed_file(filename):
    return " " in filename and filename.rsplit(".", 1)[1] not in ALLOWED_EXTENSIONS
@app.route('/', methods=["GET", "POST"]) #Configuramos la ruta de indice
def index():
    if request.method == "POST": #Si el usuario apreta el boton del formulario
        mail = request.form.get('email') #Obtenemos el valor del campo con nombre emal
        password = request.form.get('pass') #Obtenemos el valor del campo pass
        
        if mail == '' or password == '':
            msg = "No dejes campos en blanco"
            flash(msg)
        else:
            mongo_resp = registrarDB.return_confirmed(mail, password)
            print(mongo_resp)
            if type(mongo_resp) == tuple:
                if mongo_resp[0] == True:
                    session['mail'] = mongo_resp[2]
                    return redirect(url_for('rellenarPerfil'))
            else:
                if mongo_resp == False:
                    session['register'] = True
                    return redirect(url_for('confirm'))
                elif mongo_resp == 3:
                    return redirect(url_for('register'))
                elif mongo_resp == 4:
                    msg = "Revisa tu contraseña y/o usuario"
                    flash(msg)
        #TODO: comparacion de contraseñas
        #return redirect(url_for('login')) #Redireccionamos al metodo login que esta mas abajo
    
    return render_template('login/index.html', titulo='Incio') #Cuando el metodo sea GET renderizamos la template index.html

@app.route('/register', methods=["GET", "POST"]) #Configuramos la ruta register
def register(): 
    if request.method == "POST": #Si se presiona el boton del formulario
        mail = request.form.get('email') #Se obtiene el valor del campo con nombre email
        password = request.form.get('pass') #Se obtiene el valor del campo con nombre pass
        confirm_pass = request.form.get('pass2') # Se obtiene el valor del campo pass2
        if not "@" in mail:
            not_valid = "El mail no es valido"
            flash(not_valid)
        else:
            if (mail == '') or (password == '') or (confirm_pass == ''):
                blank_info = 'Debes rellenar todos los campos'
                flash(blank_info)
            else: 
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
    return render_template('login/register.html') # Si el metodo es get retornamos la template

@app.route('/confirm', methods=["GET"]) #Configuramos la ruta
def confirm(): 
    if "register" in session: #Comprobamos si el usuario termino el registro
        session.pop('register', None) #Quitamos la cookie de registro
        return render_template('login/confirm.html', titulo="Confirma tu correo") #Devolvemos el template de confirm
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
        return render_template('login/gracias.html', titulo="Gacias :)") #Enviamos el html al navegador
    else: #Si npo esta la cookie
        return "Algo ha salido mal :(" #Enviamos una string al navegador



@app.route('/completar_perfil', methods=["GET", "POST"])
def rellenarPerfil():
    if request.method == "POST":
        if "miArchivo" not in request.files:
            mensaje = "Deves subir un archivo"
            flash(mensaje)
        else:    
            f = request.files['miArchivo']
            if f.filename == '':
                mensaje = "Debes seleccionar un archivo"
                flash(mensaje)
            elif f and allowed_file(f.filename):
                mensaje = "El archivo deve ser una imagen"
                flash(mensaje)
            else:
                filename = secure_filename(f.filename)

                f.save(os.path.join(app.config["PROFILE_UPLOAD_FOLDER"], filename))
                perfil.ingresarNuevo(session.get('mail'), image_url=url_for('static', filename="profileImages/"+filename))
                session.mail = session.get('mail')
                return redirect(url_for('rellenarPerfil'))

    if request.method == "GET":
        
        if not 'mail' in session:
            return "Error al procesar los datos"
        else:
            myQuery = perfil.perfilFind(session.get('mail'))
            if not myQuery:     
                session['mail'] = session.get('mail')
                return render_template('main/personalizar.html')
            else:
                image_url = myQuery['image_url']
                return render_template('main/personalizar.html', link=image_url)
        
@app.route('/rellenar_paso2', methods=['GET', 'POST'])
def rellenarPaso2():
    if request.method == "POST":
        nickname = request.form.get('nickname')
        bio = request.form.get('bio')
        perfil.ingresarNuevo(session.get('mail'), nickname=nickname, biography=bio)
        session['mail'] = session.get('mail')
        return redirect(url_for('verPerfil'))
    if not 'mail' in session:
        return "Error al procesar los datos"
    else:
        myQuery = perfil.perfilFind(session.get('mail'))
        if not myQuery:
            return render_template('main/personalizar_s2.html')
        else:
            image_url = myQuery['image_url']
            return render_template('main/personalizar_s2.html', link=image_url)
@app.route('/ver_perfil')
def verPerfil():
    if 'mail' in session:
        myQuery = perfil.perfilFind(session.get('mail'))
        nickname = myQuery['nickname']
        bio = myQuery['biography']
        print(myQuery)
        image_url = myQuery['image_url']
        return render_template('main/ver_perfil.html', nickname=nickname, biografia=bio, link=image_url)
    else:
        return "Error"
#@app.route('/login') #Configuramos la ruta login
#def login():
#    if 'mail' in session: #Si la sesion contiene un mail
#        mail = session.get('mail') #Obtenemos el email de las cookies
#        password = session.get('password')
#        session.pop('password', None)
#        mongoResp = registrarDB.return_confirmed(mail, password) #Comprobamos si esta confirmado
#        if mongoResp[0] == True: #Si esta confirmado
#            return "bienvenido: "+mail #Le damos una bienvenida
#            #TODO: Pagina de incio de usuario
#        elif mongoResp[0] == False: #Si la respuesta de mongo es falsa
#             # Quitamos el mail de las cookies
#            session['register'] = True # Ponemos la cooke para mostrar la pagina para confirmar mail
#            session.pop('mail', None)
#            return redirect(url_for('confirm'))
#        elif mongoResp[0] == 3: #Si el usuario no esta registrado
            #Quitamos el mail de las cookies
            #TODO: Autorellenado de formulario
#            session.pop('mail', None)
#            return redirect(url_for('register')) #Y lo redireccionamos a la pagina de registro
#    else: #Si no tiene un mail
#        return "Algo salio mal :(" #Enviamos un string al navegador

        
    
if __name__ == '__main__': #Si lo ejecutamos desde este archivo
    app.run(debug=True) #Corremos la aplicacion en modo debug
    