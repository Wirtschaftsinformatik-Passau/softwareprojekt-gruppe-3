from flask import Blueprint, render_template, request
from .database import mysql
import re
# store the standard routes for a website where the user can navigate to
auth = Blueprint('auth', __name__)
@auth.route('anmelden', methods = ['POST', 'GET'])
def anmelden():
    return render_template("anmelden.html")


@auth.route('/logout')
def logout():
    return render_template("logout.html")
@auth.route('/registrieren', methods= ['GET', 'POST'])
def registrieren():
    msg = ''
    if request.method == 'POST' and 'vorname' in request.form and 'nachname' in request.form and 'emailAdresse' in request.form and 'passwort' in request.form:
        vorname = request.form['vorname']
        nachname = request.form['nachname']
        emailAdresse= request.form['emailAdresse']
        passwort= request.form['passwort']

        cursor= mysql.get_db().cursor()
        cursor.execute('SELECT * FROM nutzerkonto WHERE emailAdresse = % s', (emailAdresse,))
        konto = cursor.fetchone()
        if konto:
            msg = 'Konto existiert bereits !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', emailAdresse):
            msg = 'Ungültige E-Mail-Adresse !'
        elif not re.match(r'[A-Za-z0-9]+', passwort):
            msg = 'Das Passwort darf nur Buchstaben und Zahlen enthalten!'
        elif not vorname or not nachname or not emailAdresse or not passwort:
            msg = 'Bitte füllen Sie das Formular aus !'
        else:
            cursor.execute('INSERT INTO nutzerkonto VALUES (NULL, % s, % s, % s, % s , "Passagier")', (vorname, nachname, emailAdresse , passwort ))
            mysql.get_db().commit()
            msg = 'Sie haben sich erfolgreich registriert !'
    elif request.method == 'POST':
        msg = 'Bitte füllen Sie das Formular aus !'
    return render_template('registrieren.html', msg=msg)


