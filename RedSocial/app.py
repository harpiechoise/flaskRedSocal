from flask import Flask, render_template, request, flash, redirect, url_for
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
    MAIL_USERNAME = 'email',
    MAIL_PASSWORD = 'contraseña',
))
mailServer.init_app(app)
app.secret_key = os.urandom(32)
@app.route('/', methods=["GET", "POST"])
def index():
    if request.method == "POST":
        print(request.form['pass'])
        print(request.form['email'])
    
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
           print(user_id)
           link = "http://127.0.0.1:5000/confirm_step/{}".format(user_id)
           print(mail)

           msg = Message("Confirma tu mail", sender='jcrispis56@gmail.com', recipients=[mail], body="Hola {} te damos la bienvenida a la pagina para confirmar sigue este link: \n{}".format(mail, link))
           mailServer.send(msg)
           return redirect(url_for('confirm'))
    return render_template('register.html')

@app.route('/confirm', methods=["GET"])
def confirm():
    return render_template('confirm.html')

if __name__ == '__main__':
    app.run(debug=True)
    