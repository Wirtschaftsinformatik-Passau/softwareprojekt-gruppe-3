from flask import Blueprint, render_template,request,redirect,url_for,flash
from . import db
from .models import Nutzerkonto
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import re
import string









# store the standard routes for a website where the user can navigate to

auth = Blueprint('auth', __name__)


@auth.route('/registrieren', methods=['GET', 'POST'])
def registrieren():
    if request.method == 'POST':
        vorname = request.form.get("vorname")
        nachname = request.form.get("nachname")
        emailadresse = request.form.get("emailadresse")
        passwort1 = request.form.get("passwort1")
        passwort2 = request.form.get("passwort2")

        konto = Nutzerkonto.query.filter_by(emailadresse=emailadresse).first()
        if konto:
            flash('Konto existiert bereits !', category='error')
        elif passwort1 != passwort2:
            flash('Passwort stimmt nicht überein!', category='error')
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', emailadresse):
            flash('Ungültige Email Adresse !', category='error')
        elif not re.match (r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&/+])[A-Za-z\d@$!%*#?&/+]{8,}$', passwort1):
            flash('Passwort muss mindestens 8 Zeichen lang sein und mindestens eine Zahl und ein Sonderzeichen enthalten!', category='error')

        else:
            # Create a new user and add them to the database
            user = Nutzerkonto(vorname=vorname, nachname=nachname, emailadresse=emailadresse,

                                  passwort=generate_password_hash(passwort1, method='sha256'), rolle="Passagier")
            db.session.add(user)
            db.session.commit()
            # Log the user in
            login_user(user, remember=True)
            flash('Sie haben sich erfolgreich registriert !', category='success')

            return redirect(url_for('views.home'))

    return render_template("user_authentification/registrieren.html", user=current_user)


@auth.route('anmelden', methods=['GET', 'POST'])
def anmelden():
    if request.method == 'POST':
        emailadresse = request.form.get('emailadresse')
        passwort = request.form.get('passwort')

        nutzer = Nutzerkonto.query.filter_by(emailadresse=emailadresse).first()
        if nutzer:
            # Note: the password length should be changed to 255 charachters in the database & in Nutzerkonto Model
            if check_password_hash(nutzer.passwort, passwort) and nutzer.rolle == "Passagier":
                flash('Erfolgreich angemeldet', category='success')
                login_user(nutzer, remember=True)
                return redirect(url_for('views.home'))
            elif check_password_hash(nutzer.passwort, passwort) and nutzer.rolle == "Verwaltungspersonal":
                flash('Erfolgreich angemeldet', category='success')
                login_user(nutzer, remember=True)
                return redirect(url_for('views.flugzeug_erstellen'))
            elif check_password_hash(nutzer.passwort, passwort) and nutzer.rolle == "Bodenpersonal":
                flash('Erfolgreich angemeldet', category='success')
                login_user(nutzer, remember=True)
                return redirect(url_for('views.flugzeug_erstellen')) # should be changed later
            else:
                flash(' Passwort oder Email Adresse ist falsch! Versuchen Sie es erneut.', category='error')
        else:
            flash('Die E-Mail Adresse existiert nicht.', category='error')

    return render_template("user_authentification/anmelden.html")




@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Du bist jetzt abgemeldet!', category='success')
    return redirect(url_for('auth.anmelden'))


@auth.route('/Profil', methods=['GET'])
def Profil():
    user = Nutzerkonto.query.get(current_user.id)
    return render_template("user_authentification/profil.html", user=user)

@auth.route('/passwort_aendern', methods=['GET','POST'])
def passwort_aendern() :
    if request.method == 'POST':
        # Get the old password and the new password from the form
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        # Check that the new password meets the requirements
        if not re.search(r'[0-9]', new_password):
            flash('Neues Passwort muss mindestens eine Ziffer enthalten.', category='error')
            return render_template("user_authentification/passwort_aendern.html")
        if not re.search(r'[^A-Za-z0-9]', new_password):
            flash('Neues Passwort muss mindestens ein Sonderzeichen enthalten.', category='error')
            return render_template("user_authentification/passwort_aendern.html")
        if len(new_password) < 8:
            flash('Neues Passwort muss mindestens 8 Zeichen lang sein.', category='error')
            return render_template("user_authentification/passwort_aendern.html")
        if new_password != confirm_password:
            flash('Neues Passwort und Passwort wiederholen stimmen nicht überein.', category='error')
            return render_template("user_authentification/passwort_aendern.html")

            # Check that the old password is correct
        if not check_password_hash(current_user.passwort, current_password):
            flash('Altes Passwort ist falsch!.', category='error')
            return render_template("user_authentification/passwort_aendern.html")

            # Hash the new password and update the user's password in the database
        current_user.passwort = generate_password_hash(new_password)
        db.session.commit()
        #logout user after password_aendern and then he would be redirected to the home page
        logout_user()
        flash('Passwort wurde erfolgreich geändert! Jetzt erneut anmelden.', category='success')
        return redirect(url_for('auth.anmelden'))  # maybe it'd better to be redirected to the anmelden page!!


    return render_template("user_authentification/passwort_aendern.html")


#passwort_vergessen




