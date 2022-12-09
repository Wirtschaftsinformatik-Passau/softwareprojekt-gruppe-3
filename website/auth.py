from flask import Blueprint, render_template, request,session,redirect, url_for
from .database import mysql
import re


# store the standard routes for a website where the user can navigate to
auth = Blueprint('auth', __name__)


@auth.route('/einloggen', methods = ['POST', 'GET'])
def einloggen():
    msg = ''
    if request.method == 'POST' and 'emailAdresse' in request.form and 'passwort' in request.form:
        emailAdresse = request.form['emailAdresse']
        passwort = request.form['passwort']
        # Check if account exists using MySQL
        cursor = mysql.get_db().cursor()
        cursor.execute('SELECT * FROM nutzerkonto WHERE emailAdresse = %s AND passwort = %s', (emailAdresse, passwort,))
        # Fetch one record and return result
        account = cursor.fetchone()
        # If account exists in accounts table in out database
        if account:
            session['loggedin'] = True
            session['id'] = account[0]
            session['email'] = account[3]
            return 'Erfolgreich eingeloggt!'
        else:
            # Account doesnt exist or EmailAdresse/passwort incorrect
            msg = 'Email Adresse/passwort ist nicht korrekt !'

    return render_template("einloggen.html",msg=msg)


@auth.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('email', None)
    # Redirect to login page
    return redirect(url_for('auth.einloggen'))



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
        account = cursor.fetchone()
        if account:
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


