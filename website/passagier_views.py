from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import current_user, login_required
from werkzeug.security import generate_password_hash
from . import db
from .models import Flug, Flughafen, Flugzeug, Nutzerkonto, Buchung, Passagier, Gepaeck
from sqlalchemy.sql import text
from sqlalchemy import or_, cast, Date

# store the standard routes for a website where the user can navigate to
passagier_views = Blueprint('passagier_views', __name__)

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

# Passagierfunktionen
@passagier_views.route('/buchung_suchen', methods=['GET', 'POST'])
def buchung_suchen():
    #globale Definition, damit sich die BuchungsID im Online Check In gemerkt wird
    global input_buchungsid
    input_buchungsid=request.args.get('buchungsid')
    #ANMERKUNG: input_buchungsid wird verwendet, damit im Online Check in auf den Passagier zugegriffen werden kann

    buchung = Buchung.query.filter(Buchung.buchungsid == input_buchungsid)
    # Kennung des Ankunftflughafens
    ankunft_flughafen = Flughafen.query.filter(Buchung.flugid == Flug.flugid).where(
        Flug.abflugid == Flughafen.flughafenid).where(Buchung.buchungsid == input_buchungsid)
    # Kennung des Zielflughafens
    ziel_flughafen = Flughafen.query.filter(Buchung.flugid == Flug.flugid).where(
        Flug.zielid == Flughafen.flughafenid).where(Buchung.buchungsid == input_buchungsid)
    nutzer = Nutzerkonto.query.filter(
        Buchung.nutzerid == Nutzerkonto.id).where(Buchung.buchungsid == input_buchungsid)
    flug = Flug.query.filter(Flug.flugid == Buchung.flugid).where(Buchung.buchungsid == input_buchungsid)
    gepaeck = Gepaeck.query.all()

    return render_template('Passagier/buchung_suchen.html', buchung=buchung, ankunft_flughafen=ankunft_flughafen,
                           ziel_flughafen=ziel_flughafen, flug=flug, user=current_user, nutzer=nutzer, gepaeck=gepaeck)

def set_buchungsid(input_buchungsid):
    buchungsid = input_buchungsid

def get_buchungsid():
    return input_buchungsid

@passagier_views.route('/protected')
@login_required
def get_logged_in_user():
  # Get the currently logged-in user
  user = current_user
  print(user.vorname, user.nachname)


@passagier_views.route('/online_check_in', methods=['POST', 'GET'])
def online_check_in():
    #FEHLERMELDUNG war: 'Query' object has no attribute 'buchungsid'-> LÖSUNG: .first() hinzufügen
    passagier = Passagier.query.filter(get_buchungsid() == Passagier.buchungsid).first()
    #MÖGLICHER ERROR Checkin: NutzerID & PassagierID, wenn die Buchung dieselbe ist.
    ausweistyp = request.args.get("ausweistyp")
    db.session.commit()
    ausweissnummer = request.args.get("ausweissnummer")
    db.session.commit()
    ausweisgueltigkeit = request.args.get("ausweisgueltigkeit")
    db.session.commit()
    print(ausweisgueltigkeit)
    print(ausweissnummer)
    print(ausweistyp)

    #FEHLT: Prüfung ob eingeloggter Nutzer auch Passagier ist
    return render_template("Passagier/online_check_in.html", passagier=passagier, ausweisgueltigkeit=ausweisgueltigkeit, ausweistyp=ausweistyp, ausweissnummer=ausweissnummer)

@passagier_views.route('/storno')
def storno():
    return render_template('Passagier/storno.html', user=current_user)


@passagier_views.route('/gepaecksbestimmungen', methods=['GET'])
def gepaecksbestimmungen_anzeigen():
    return render_template("Passagier/gepaecksbestimmungen.html", user=current_user)
