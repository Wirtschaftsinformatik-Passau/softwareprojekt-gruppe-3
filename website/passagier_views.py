from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import current_user, login_required
from werkzeug.security import generate_password_hash
from . import db
from .models import Flug, Flughafen, Flugzeug, Nutzerkonto, Buchung, Passagier, Gepaeck
from sqlalchemy import or_, cast, Date

# store the standard routes for a website where the user can navigate to
passagier_views = Blueprint('passagier_views', __name__)

check_in_user=""
def set_check_in_user(user):
    check_in_user = user

def get_check_in_user():
    return check_in_user
# Passagierfunktionen
@passagier_views.route('/flug-buchen/<int:id>/<int:anzahlPassagiere>', methods=['GET', 'POST'])
@login_required
def flug_buchen(id, anzahlPassagiere):
    if request.method == 'POST':
        neue_buchung = Buchung(nutzerid=current_user.id, flugid=id, buchungsstatus="gebucht",
                               buchungsnummer=current_user.id + id + 1234)
        db.session.add(neue_buchung)
        db.session.commit()

        if anzahlPassagiere == 1:
            vorname = request.form['vorname']
            nachname = request.form['nachname']
            geburtsdatum = request.form['geburtsdatum']
            neuer_passagier = Passagier(buchungsid=neue_buchung.buchungsid, vorname=vorname, nachname=nachname,
                                        geburtsdatum=geburtsdatum, passagierstatus="gebucht")
            db.session.add(neuer_passagier)
            db.session.commit()
            flash('Buchung erfolgreich', category='success')
            return redirect(url_for('views.home'))

        if anzahlPassagiere == 2:
            vorname = request.form['vorname']
            nachname = request.form['nachname']
            geburtsdatum = request.form['geburtsdatum']
            neuer_passagier = Passagier(buchungsid=neue_buchung.buchungsid, vorname=vorname, nachname=nachname,
                                        geburtsdatum=geburtsdatum, passagierstatus="gebucht")

            vorname1 = request.form['vorname1']
            nachname1 = request.form['nachname1']
            geburtsdatum1 = request.form['geburtsdatum1']
            neuer_passagier1 = Passagier(buchungsid=neue_buchung.buchungsid, vorname=vorname1, nachname=nachname1,
                                         geburtsdatum=geburtsdatum1, passagierstatus="gebucht")

            db.session.add(neuer_passagier)
            db.session.add(neuer_passagier1)
            db.session.commit()
            flash('Buchung erfolgreich', category='success')
            return redirect(url_for('views.home'))

    return render_template("Passagier/flug_buchen.html", user=current_user, flugid=id,
                           anzahlPassagiere=anzahlPassagiere)


@passagier_views.route('/protected')
@login_required
def get_logged_in_user():
  # Get the currently logged-in user
  user = current_user
  print(user.vorname, user.nachname)

@passagier_views.route('/buchung_suchen', methods=['GET', 'POST'])
def buchung_suchen():
    input_buchungsnummer = request.args.get('buchungsnummer')

    buchung = Buchung.query.filter(Buchung.buchungsnummer == input_buchungsnummer)
    # Kennung des Ankunftflughafens
    ankunft_flughafen = Flughafen.query.filter(Buchung.flugid == Flug.flugid).where(
        Flug.abflugid == Flughafen.flughafenid).where(Buchung.buchungsnummer == input_buchungsnummer)
    # Kennung des Zielflughafens
    ziel_flughafen = Flughafen.query.filter(Buchung.flugid == Flug.flugid).where(
        Flug.zielid == Flughafen.flughafenid).where(Buchung.buchungsnummer == input_buchungsnummer)
    nutzer = Nutzerkonto.query.filter(
        Buchung.nutzerid == Nutzerkonto.id).where(Buchung.buchungsnummer == input_buchungsnummer)
    set_check_in_user(nutzer)
    flug = Flug.query.filter(Flug.flugid == Buchung.flugid).where(Buchung.buchungsnummer == input_buchungsnummer)
    gepaeck = Gepaeck.query.all()

    return render_template('Passagier/buchung_suchen.html', buchung=buchung, ankunft_flughafen=ankunft_flughafen,
                           ziel_flughafen=ziel_flughafen, flug=flug, user=current_user, nutzer=nutzer, gepaeck=gepaeck)


@passagier_views.route('/online_check_in', methods=['POST', 'GET'])
def online_check_in():
    #get_check_in_user()
    get_logged_in_user() #gibt Vor- und Nachname des Nutzers zurück
    #Prüfung ob eingeloggter Nutzer auch Passagier ist
    #geburtsdatum = Passagier.query.filter(current_user.vorname == Passagier.vorname).where(current_user.nachname == Passagier.nachname).where(Nutzerkonto.rolle=="Passagier")
    return render_template("Passagier/online_check_in.html", user=current_user)

@passagier_views.route('/storno')
def storno():
    return render_template('Passagier/storno.html', user=current_user)


@passagier_views.route('/gepaecksbestimmungen', methods=['GET'])
def gepaecksbestimmungen_anzeigen():
    return render_template("Passagier/gepaecksbestimmungen.html", user=current_user)
