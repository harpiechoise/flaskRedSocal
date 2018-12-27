from flask import Flask, session, render_template, request, redirect, url_for, g
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)
@app.route('/', methods=["GET", "POST"])
def index():
    session.pop('user', None)
    if request.method == "POST":
        if request.form['password'] == 'pass':
            session['user'] = request.form['user']
            return redirect(url_for('protected'))

    return render_template('index.html')

@app.route('/protected')
def protected():
    if g.user:
        return 'Welcome to the protected page'
    return redirect(url_for('index'))
@app.before_request
def before_request():
    g.user = None
    if 'user' in session:
        g.user = session['user']


@app.route('/getsession')
def getSession():
    if 'user' in session:
        return session['user']
    return 'Setteado'

@app.route('/drop')
def drop():
    session.pop('user', None)
    return 'Dropped'
if __name__ == '__main__':
    app.run(debug=True)