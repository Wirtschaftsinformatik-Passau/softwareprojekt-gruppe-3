import re

from flask import Blueprint, render_template, request, redirect, url_for, flash
from . import db
from .models import Nutzerkonto
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import re, string

# store the standard routes for a website where the user can navigate to
nutzer_mit_account_views = Blueprint('nutzer_mit_account_views', __name__)

MINIMALE_PASSWORTLÄNGE = 8

@nutzer_mit_account_views.route('anmelden', methods=['GET', 'POST'])
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
                return redirect(url_for('views.flugzeug_erstellen'))  # should be changed later
            else:
                flash(' Passwort oder Email Adresse ist falsch! Versuchen Sie es erneut.', category='error')
        else:
            flash('Die E-Mail Adresse existiert nicht.', category='error')

    return render_template("nutzer_mit_account/anmelden.html")


@nutzer_mit_account_views.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Du bist jetzt abgemeldet!', category='success')
    return redirect(url_for('nutzer_mit_account_views.anmelden'))


@nutzer_mit_account_views.route('/profil', methods=['GET'])
def profil():
    user = Nutzerkonto.query.get(current_user.id)
    return render_template("nutzer_mit_account/profil.html", user=user)


@nutzer_mit_account_views.route('/passwort_aendern', methods=['GET', 'POST'])
def passwort_aendern():
    if request.method == 'POST':
        # Get the old password and the new password from the form
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        # Check that the new password meets the requirements
        if not re.search(r'[0-9]', new_password):
            flash('Neues Passwort muss mindestens eine Ziffer enthalten.', category='error')
            return render_template("nutzer_mit_account/passwort_aendern.html")
        if not re.search(r'[^A-Za-z0-9]', new_password):
            flash('Neues Passwort muss mindestens ein Sonderzeichen enthalten.', category='error')
            return render_template("nutzer_mit_account/passwort_aendern.html")
        if len(new_password) < MINIMALE_PASSWORTLÄNGE:
            flash('Neues Passwort muss mindestens 8 Zeichen lang sein.', category='error')
            return render_template("nutzer_mit_account/passwort_aendern.html")
        if new_password != confirm_password:
            flash('Neues Passwort und Passwort wiederholen stimmen nicht überein.', category='error')
            return render_template("nutzer_mit_account/passwort_aendern.html")

            # Check that the old password is correct
        if not check_password_hash(current_user.passwort, current_password):
            flash('Altes Passwort ist falsch!.', category='error')
            return render_template("nutzer_mit_account/passwort_aendern.html")

            # Hash the new password and update the user's password in the database
        current_user.passwort = generate_password_hash(new_password)
        db.session.commit()
        # logout user after password_aendern and then he would be redirected to the home page
        logout_user()
        flash('Passwort wurde erfolgreich geändert! Jetzt erneut anmelden.', category='success')
        return redirect(url_for('nutzer_mit_account_views.anmelden'))  # maybe it'd better to be redirected to the anmelden page!!

    return render_template("nutzer_mit_account/passwort_aendern.html")

# passwort_vergessen