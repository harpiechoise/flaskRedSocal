from flask import Flask, render_template, request, flash, redirect, url_for, session
from flask_mail import Mail, Message
import os
from dbUtils import register as registrarDB

mailServer = Mail()
app = Flask(__name__)
app.config.update(dict(
    DEBUG = True,
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = 587,
    MAIL_USE_TLS = True,
    MAIL_USE_SSL = False,
    MAIL_USERNAME = 'mail',
    MAIL_PASSWORD = 'contraseña',
))
mailServer.init_app(app)
app.secret_key = os.urandom(32)
@app.route('/', methods=["GET", "POST"])
def index():
    if request.method == "POST":
        session['mail'] = request.form.get('email')
        return redirect(url_for('login'))
    
    return render_template('index.html')

@app.route('/register', methods=["GET", "POST"])
def register():
    mail = request.form.get('email')
    password = request.form.get('pass')
    confirm_pass = request.form.get('pass2')
    if request.method == "POST":
        if not password == confirm_pass:
            password_error = 'Las contaseñas no coinciden'
            flash(password_error)
        else:
           user_id = registrarDB.registrar_usuario(mail, password)
           if not user_id:
               pass
           else: 
            print(user_id)
            link = "http://127.0.0.1:5000/confirm_step/{}".format(user_id)
            print(mail)

            msg = Message("Confirma tu mail", sender='jcrispis56@gmail.com', recipients=[mail], body="Hola {} te damos la bienvenida a la pagina para confirmar sigue este link: \n{}".format(mail, link))
            mailServer.send(msg)
            session['register'] = True
            return redirect(url_for('confirm'))
    return render_template('register.html')

@app.route('/confirm', methods=["GET"])
def confirm():
    if "register" in session:
        session.pop('register', None)
        return render_template('confirm.html')
    else:
        return "Algo ha salido mal :("
@app.route('/confirm_step/<RegID>')
def confirm_step(RegID):
    RegID = str(RegID)

    confirmacion = registrarDB.confirmar(RegID)
    if not confirmacion:
        return "Hubo un error en procesar los datos vuelva a intentarlo"
    else:
        session['Redirected'] = True
        return redirect(url_for('gracias'))
    return " "

@app.route('/gracias')
def gracias():
    if 'Redirected' in session:
        session.pop("Redirected", None)
        return render_template('gracias.html')
    else: 
        return "Algo ha salido mal :("

@app.route('/login')
def login():
    if 'mail' in session:
        mail = session.get('mail')
        mongoResp = registrarDB.return_confirmed(mail)
        if mongoResp[0] == True:
            session.pop('mail', None)
            return "bienvenido: "+mail
        elif mongoResp[0] == False:
            session.pop('mail', None)
            session['register'] = True
            return redirect(url_for('confirm'))
        elif mongoResp[0] == 3:
            session.pop('mail', None)
            return redirect(url_for('register'))
    else:
        return "Algo salio mal :("

        
    
if __name__ == '__main__':
    app.run(debug=True)
    