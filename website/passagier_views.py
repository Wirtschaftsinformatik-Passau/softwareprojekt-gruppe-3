from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import current_user, login_required
from werkzeug.security import generate_password_hash
from . import db
from .models import Flug, Flughafen, Flugzeug, Nutzerkonto, Buchung, Passagier, Gepaeck, Rechnung
from sqlalchemy import or_, cast, Date
import string
import random
from datetime import date

# store the standard routes for a website where the user can navigate to
passagier_views = Blueprint('passagier_views', __name__)


# Id generator für Buchungsnummer
def id_generator(size=8, chars=string.ascii_uppercase):
    return ''.join(random.choice(chars) for _ in range(size))


# Passagierfunktionen
@passagier_views.route('/flug-buchen/<int:id>/<int:anzahlPassagiere>', methods=['GET', 'POST'])
@login_required
def flug_buchen(id, anzahlPassagiere):
    buchung_preis = Flug.query.filter_by(flugid=id).first().preis * anzahlPassagiere
    print(buchung_preis)
    zusatzgepaeck_counter = 0

    if request.method == 'POST':
        # neue Buchung erstellen
        neue_buchung = Buchung(nutzerid=current_user.id, flugid=id, buchungsstatus="gebucht",
                               buchungsnummer=id_generator())

        db.session.add(neue_buchung)
        db.session.commit()

        # liste mit den passagierdaten erstellen, maximale länge = 4 -> für jeden passagier neuer eintrag

        passagier_data = []

        max_items_per_list = 4

        # schleife iteriert über bis alle liste 4 einträge hat. dann wird ein neues passagier erstellt sowie für jeden
        # Passagier die anzahl an ausgewählten gepäckstücken

        for key, value in request.form.items():
            passagier_data.append(value)
            if len(passagier_data) == max_items_per_list:
                neuer_passagier = Passagier(buchungsid=neue_buchung.buchungsid, vorname=passagier_data[0],
                                            nachname=passagier_data[1], geburtsdatum=passagier_data[2],
                                            boardingpassnummer=neue_buchung.buchungsnummer + str(random.randint(10, 99)))

                db.session.add(neuer_passagier)
                db.session.commit()

                # für jeden Passagier wird für die Anzahl an ausgewählte Gepäckstücken ein eintrag erstellt

                for count in range(int(passagier_data[3])):
                    neues_gepaeck = Gepaeck(passagierid=neuer_passagier.passagierid, gewicht=40, status="gebucht")
                    db.session.add(neues_gepaeck)
                    db.session.commit()
                    zusatzgepaeck_counter = zusatzgepaeck_counter + 1
                passagier_data = []

        #neuen preis berechnen

        rechnungs_preis = (Flug.query.filter_by(flugid=id).first().preis * anzahlPassagiere) + (zusatzgepaeck_counter * 40)

        #neue rechnung erstellen

        neue_rechnung = Rechnung(buchungsid=neue_buchung.buchungsid,
                                 rechnungsnummer=date.today().strftime("%d%m%Y") + neue_buchung.buchungsnummer,
                                 status="bezahlt",
                                 betrag=rechnungs_preis,
                                 rechnungsinhalt="Ihre Rechnung")
        db.session.add(neue_rechnung)
        db.session.commit()

        flash('Buchung erfolgreich', category='success')

        return redirect(url_for('nutzer_ohne_account_views.home'))

    return render_template("Passagier/flug_buchen.html", user=current_user, flugid=id,
                           anzahlPassagiere=anzahlPassagiere, preis=buchung_preis)


@passagier_views.route('/online_check_in', methods=['POST', 'GET'])
def online_check_in():
    return render_template("Passagier/online_check_in.html", user=current_user)


@passagier_views.route('/buchung_suchen', methods=['GET', 'POST'])
def buchung_suchen():
    input_buchungsnummer = request.form.get('buchungsnummer')

    buchung = Buchung.query.filter(Buchung.buchungsnummer == 999)
    # Kennung des Ankunftflughafens
    ankunft_flughafen = Flughafen.query.filter(Buchung.flugid == Flug.flugid).where(
        Flug.abflugid == Flughafen.flughafenid).where(Buchung.buchungsnummer == 999)
    # Kennung des Zielflughafens
    ziel_flughafen = Flughafen.query.filter(Buchung.flugid == Flug.flugid).where(
        Flug.zielid == Flughafen.flughafenid).where(Buchung.buchungsnummer == 999)
    nutzer = Nutzerkonto.query.filter(
        Buchung.nutzerid == Nutzerkonto.id).where(Buchung.buchungsnummer == 999)
    flug = Flug.query.filter(Flug.flugid == Buchung.flugid).where(Buchung.buchungsnummer == 999)
    gepaeck = Gepaeck.query.all()

    return render_template('Passagier/buchung_suchen.html', buchung=buchung, ankunft_flughafen=ankunft_flughafen,
                           ziel_flughafen=ziel_flughafen, flug=flug, user=current_user, nutzer=nutzer, gepaeck=gepaeck)


@passagier_views.route('/storno')
def storno():
    return render_template('Passagier/storno.html', user=current_user)


@passagier_views.route('/gepaecksbestimmungen', methods=['GET'])
def gepaecksbestimmungen_anzeigen():
    return render_template("Passagier/gepaecksbestimmungen.html", user=current_user)
