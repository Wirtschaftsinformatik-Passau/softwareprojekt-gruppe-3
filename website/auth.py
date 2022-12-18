from flask import Blueprint, render_template,request,redirect,url_for,flash
from . import db
from .models import Nutzerkonto
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import re







# store the standard routes for a website where the user can navigate to

auth = Blueprint('auth', __name__)




@auth.route('/anmelden', methods=['GET', 'POST']) # mit Rolle
def anmelden():
    if request.method == 'POST':
        emailadresse = request.form.get("emailadresse")
        passwort = request.form.get("passwort")

        nutzer = Nutzerkonto.query.filter_by(emailadresse=emailadresse).first()
        if nutzer:
            if check_password_hash(nutzer.passwort, passwort):
                flash("Logged in!", category='success')
                login_user(nutzer, remember=True)
                #return redirect(url_for('views.home'))
            else:
                flash('Password is incorrect.', category='error')
        else:
            flash('Email does not exist.', category='error')
    return render_template("user_authentification/anmelden.html")


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("views.home"))


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
        elif not re.match(r'[A-Za-z0-9]+', passwort1):
            flash('Das Passwort darf nur Buchstaben und Zahlen enthalten!', category='error')
        elif not vorname or not nachname or not emailadresse or not passwort1 or not passwort2:
            flash('Bitte füllen Sie das Formular aus !', category='error')
        elif not len(passwort1) >= 8:
            flash('Das Passwort muss mindestens 8 Zahlen beinhalten ', category='error')
        else:
            new_user = Nutzerkonto(vorname=vorname,nachname=nachname,emailadresse=emailadresse,\
                                   passwort=generate_password_hash(passwort1, method='sha256'),rolle="Passagier")
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Sie haben sich erfolgreich registriert !', category='success')
            #return redirect(url_for('views.home'))
    return render_template("user_authentification/registrieren.html")







