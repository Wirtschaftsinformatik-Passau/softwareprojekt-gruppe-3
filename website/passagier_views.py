from sqlalchemy.sql.expression import text
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import current_user, login_required
from werkzeug.security import generate_password_hash
from . import db
from .models import Flug, Flughafen, Flugzeug, Nutzerkonto, Buchung, Passagier, Gepaeck, Rechnung
from sqlalchemy import or_, cast, Date
import string
import random
from datetime import date
import pprint

# store the standard routes for a website where the user can navigate to
passagier_views = Blueprint('passagier_views', __name__)

PREIS_FÜR_EIN_AUFGABEGEPÄCK = 40
MIN_ZIFFERN_REISEPASS = 9
MIN_ZIFFERN_AUSWEIS = 4


# Id generator für Buchungsnummer
def id_generator(size=8, chars=string.ascii_uppercase):
    return ''.join(random.choice(chars) for _ in range(size))


@passagier_views.route('/flug-buchen/<int:id>/<int:anzahlPassagiere>', methods=['GET', 'POST'])
@login_required
def flug_buchen(id, anzahlPassagiere):
    flug_data = Flug.query.filter_by(flugid=id).first()
    passagier_anzahl = 0
    buchung_preis = flug_data.preis * anzahlPassagiere
    print(buchung_preis)

    if request.method == 'POST':
        zusatzgepaeck_counter = 0
        # neue Buchung erstellen
        neue_buchung = Buchung(nutzerid=current_user.id, flugid=id, buchungsstatus="gebucht",
                               buchungsnummer=id_generator())

        db.session.add(neue_buchung)
        db.session.commit()

        # liste mit den passagierdaten erstellen, maximale länge = 4 -> für jeden passagier neuer eintrag

        passagier_data = []
        passagier_data_list = []

        max_items_per_list = 4

        # schleife iteriert über bis alle liste 4 einträge hat. dann wird ein neues passagier erstellt sowie für jeden
        # Passagier die anzahl an ausgewählten gepäckstücken

        for key, value in request.form.items():
            passagier_data.append(value)
            if len(passagier_data) == max_items_per_list:
                neuer_passagier = Passagier(buchungsid=neue_buchung.buchungsid, vorname=passagier_data[0],
                                            nachname=passagier_data[1], geburtsdatum=passagier_data[2],
                                            boardingpassnummer=neue_buchung.buchungsnummer + str(
                                                random.randint(10, 99)))

                db.session.add(neuer_passagier)
                db.session.commit()

                # für jeden Passagier wird für die Anzahl an ausgewählte Gepäckstücken ein Eintrag erstellt

                for count in range(int(passagier_data[3])):
                    neues_gepaeck = Gepaeck(passagierid=neuer_passagier.passagierid, gewicht=40, status="gebucht")
                    db.session.add(neues_gepaeck)
                    db.session.commit()
                    zusatzgepaeck_counter = zusatzgepaeck_counter + 1

                passagier_data_list.append(passagier_data)
                passagier_anzahl = passagier_anzahl + 1
                passagier_data = []

        # neuen preis berechnen

        rechnungs_preis = (Flug.query.filter_by(flugid=id).first().preis * anzahlPassagiere) + (
                zusatzgepaeck_counter * PREIS_FÜR_EIN_AUFGABEGEPÄCK)

        # neue rechnung erstellen
        # brutto und netto / summer der MwSt

        neue_rechnung = Rechnung(buchungsid=neue_buchung.buchungsid,
                                 rechnungsnummer=date.today().strftime("%d%m%Y") + neue_buchung.buchungsnummer,
                                 status="bezahlt",
                                 betrag=rechnungs_preis,
                                 rechnungsinhalt="Ihre Rechnung")
        db.session.add(neue_rechnung)
        db.session.commit()

        flash('Buchung erfolgreich', category='success')

        return render_template("Passagier/buchungsbestaetigung.html", user=current_user,
                               rechnungsnummer=neue_rechnung.rechnungsnummer,
                               buchungsnummer=neue_buchung.buchungsnummer,
                               passagiere=passagier_data_list, flug=flug_data, passagier_anzahl=passagier_anzahl,
                               preis=rechnungs_preis, gepaeck=zusatzgepaeck_counter)

    return render_template("Passagier/flug_buchen.html", user=current_user, flugid=id,
                           anzahlPassagiere=anzahlPassagiere, preis=buchung_preis)


# Passagierfunktionen
@passagier_views.route('/buchung_suchen', methods=['GET', 'POST'])
def buchung_suchen():
    # globale Definition, damit sich die BuchungsID im Online Check In gemerkt wird
    global input_buchungsnummer
    input_buchungsnummer = request.args.get('buchungsnummer')

    buchung = Buchung.query.filter(Buchung.buchungsnummer == input_buchungsnummer)
    # Kennung des Ankunftflughafens
    ankunft_flughafen = Flughafen.query.filter(Buchung.flugid == Flug.flugid).where(
        Flug.abflugid == Flughafen.flughafenid).where(Buchung.buchungsnummer == input_buchungsnummer)
    # Kennung des Zielflughafens
    ziel_flughafen = Flughafen.query.filter(Buchung.flugid == Flug.flugid).where(
        Flug.zielid == Flughafen.flughafenid).where(Buchung.buchungsnummer == input_buchungsnummer)
    nutzer = Nutzerkonto.query.filter(
        Buchung.nutzerid == Nutzerkonto.id).where(Buchung.buchungsid == input_buchungsnummer)
    passagier = Passagier.query.filter(Buchung.buchungsnummer == input_buchungsnummer).where(
        Buchung.buchungsid == Passagier.buchungsid)
    flug = Flug.query.filter(Flug.flugid == Buchung.flugid).where(Buchung.buchungsnummer == input_buchungsnummer)
    gepaeck = Gepaeck.query.all()

    return render_template('Passagier/buchung_suchen.html', buchung=buchung, ankunft_flughafen=ankunft_flughafen,
                           ziel_flughafen=ziel_flughafen, flug=flug, user=current_user, nutzer=nutzer,
                           gepaeck=gepaeck,
                           passagier=passagier)


def set_buchungsnummer(input_buchungsnummer):
    buchungsnummer = input_buchungsnummer


def get_buchungsnummer():
    return input_buchungsnummer


@passagier_views.route('/protected')
@login_required
def get_logged_in_user():
    # Get the currently logged-in user
    user = current_user
    print(user.vorname, user.nachname)


@passagier_views.route('/online_check_in', methods=['POST', 'GET'])
def online_check_in(vorname=None):
    #Übergabe jener Variablen aus der Buchung_suchen Funktion.
    #Abhängig von dem Button auf den geklickt wird, wird der eine oder andere Passagier ausgesucht
    buchungsnummer = request.args.get('buchungsnummer')
    vorname = request.args.get('vorname')
    nachname = request.args.get('nachname')

    #die restlichen Daten müssen nun mit jenem Passagier übereinstimmen, welcher denselben Vornamen hat.
    #Das wird erreicht durch die Überprüfung, welche Reihe zu dem Passagier gehört, auf dessen Button geklickt wurde
    passagier = Passagier.query.filter(Passagier.vorname == vorname).first()

    print(passagier , "passagier print")
    if passagier:
        if not passagier.ausweistyp:
            ausweistyp = request.args.get("ausweistyp")
            db.session.add(passagier)
            db.session.commit()
            print(ausweistyp)

            """
        IF STATEMENT FÜR LÄNGE AUSWEISNUMMER
        
        if passagier.ausweistyp=="Reisepass":
            if not len(passagier.ausweissnummer)> MIN_ZIFFERN_REISEPASS:
                flash("Bitte überprüfen Sie die Ausweisnummer")
        elif passagier.ausweistyp=="Ausweis":
            if not len(passagier.ausweisnummer)>MIN_ZIFFERN_AUSWEIS:
                flash("Bitte überprüfen Sie die Ausweisnummer")
        else:
        """
        if not passagier.ausweissnummer:
            ausweissnummer = request.args.get("ausweissnummer")
            db.session.add(passagier)
            db.session.commit()
            print(ausweissnummer)
        if not passagier.ausweisgueltigkeit:
            ausweisgueltigkeit = request.args.get("ausweisgueltigkeit")
            db.session.commit()
            print(ausweisgueltigkeit)
            print(request.args)
    else:
        flash('doenst exist')

    return render_template("Passagier/online_check_in.html", passagier=passagier, vorname=vorname, nachname=nachname)



# IF STATEMENTS
# datentypen
# nichtleere Felder
# if ausweißtyp personalausweis and len(ausweisnummer) < MINDESTLÄNGE_AUSWEISNUMMER -> falsch
# if geburtsdatum.date() > datetime.now() -> falsch
# if ausweisgueltigkeit.date() < datetime.now() -> falsch



# FEHLT: Prüfung ob eingeloggter Nutzer auch Passagier ist
# return render_template("Passagier/online_check_in.html", passagier=passagier)

@passagier_views.route('/storno')
def storno():
    return render_template('Passagier/storno.html', user=current_user)


@passagier_views.route('/gepaecksbestimmungen', methods=['GET'])
def gepaecksbestimmungen_anzeigen():
    return render_template("Passagier/gepaecksbestimmungen.html", user=current_user)
