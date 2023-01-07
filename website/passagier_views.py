import random, re
import string
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import current_user, login_required
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash
from . import mail
from . import db
from .models import Flug, Flughafen, Flugzeug, Nutzerkonto, Buchung, Passagier, Gepaeck, Rechnung
from sqlalchemy import or_, cast, Date
from datetime import date, datetime, timedelta

# store the standard routes for a website where the user can navigate to
passagier_views = Blueprint('passagier_views', __name__)


# Passagierfunktionen
# Id generator für Buchungsnummer
def id_generator(size=8, chars=string.ascii_uppercase):
    return ''.join(random.choice(chars) for _ in range(size))


# Passagierfunktionen
@passagier_views.route('/flug-buchen/<int:id>/<int:anzahlPassagiere>', methods=['GET', 'POST'])
@login_required
def flug_buchen(id, anzahlPassagiere):
    flughafen_liste = Flughafen.query.all()
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
                                            passagierstatus="gebucht",
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
                zusatzgepaeck_counter * 40)

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

        return redirect(
            url_for('passagier_views.buchungsbestaetigung', user=current_user, buchungsid=neue_buchung.buchungsid,
                    rechnungsnummer=neue_rechnung.rechnungsnummer, flugid=id,
                    buchungsnummer=neue_buchung.buchungsnummer,
                    passagiere=passagier_data_list, flug=flug_data, passagier_anzahl=passagier_anzahl,
                    preis=rechnungs_preis, gepaeck=zusatzgepaeck_counter))

    return render_template("Passagier/flug_buchen.html", user=current_user, flugid=id,
                           anzahlPassagiere=anzahlPassagiere, preis=buchung_preis)


@passagier_views.route('/buchungsbestaetigung', methods=['POST', 'GET'])
def buchungsbestaetigung():
    rechnungsnummer = request.args['rechnungsnummer']
    buchungsnummer = request.args['buchungsnummer']
    buchungsid = int(request.args['buchungsid'])
    flugid = int(request.args['flugid'])
    passagier_anzahl = int(request.args['passagier_anzahl'])
    flughafen_liste = Flughafen.query.all()
    gepaeck = int(request.args['gepaeck'])
    preis = int(request.args['preis'])
    emailadresse = Nutzerkonto.query.get_or_404(current_user.id).emailadresse
    flug_data = Flug.query.filter_by(flugid=flugid).first()

    passagiere = Passagier.query.join(Buchung).filter(Passagier.buchungsid == buchungsid).all()

    msg = Message('Buchungsbestaetigung', sender='airpassau.de@gmail.com', recipients=[emailadresse])
    msg.html = render_template("Passagier/buchungsbestaetigung_email.html", user=current_user,
                               rechnungsnummer=rechnungsnummer,
                               buchungsnummer=buchungsnummer,
                               passagiere=passagiere, flug=flug_data, passagier_anzahl=passagier_anzahl, preis=preis,
                               gepaeck=gepaeck, flughafen_liste=flughafen_liste)
    mail.send(msg)

    return render_template("Passagier/buchungsbestaetigung.html", user=current_user, rechnungsnummer=rechnungsnummer,
                           buchungsnummer=buchungsnummer,
                           passagiere=passagiere, flug=flug_data, passagier_anzahl=passagier_anzahl, preis=preis,
                           gepaeck=gepaeck, flughafen_liste=flughafen_liste)


@passagier_views.route('/online_check_in', methods=['POST', 'GET'])
def online_check_in():
    # Übergabe jener Variablen aus der Buchung_suchen Funktion.
    # Abhängig von dem Button auf den geklickt wird, wird der eine oder andere Passagier ausgesucht
    buchungsnummer = request.args.get('buchungsnummer')
    vorname = request.args.get('vorname')
    nachname = request.args.get('nachname')
    buchungsid = request.args.get('buchungsid')

    # die restlichen Daten müssen nun mit jenem Passagier übereinstimmen, welcher denselben Vornamen hat.
    # Das wird erreicht durch die Überprüfung, welche Reihe zu dem Passagier gehört, auf dessen Button geklickt wurde
    passagier = Passagier.query.filter(Passagier.buchungsid == buchungsid).where(Passagier.vorname == vorname). \
        where(Passagier.nachname == nachname).first()

    if request.method == 'POST':
        passagier.nachname = nachname
        passagier.vorname = vorname
        passagier.ausweistyp = request.form['ausweistyp']
        passagier.ausweisnummer = request.form['ausweissnummer']
        passagier.ausweisgueltigkeit = request.form['ausweisgueltigkeit']
        passagier.passagierstatus = "eingecheckt"

        db.session.commit()
        flash("Check-In erfolgreich")

        return redirect(url_for('passagier_views.buchung_suchen'))

    return render_template("Passagier/online_check_in.html", user=current_user, passagier=passagier, vorname=vorname,
                           nachname=nachname)


def is_flight_within_days(flight_time, num_days):
    # Get the current time
    current_time = datetime.now()

    # Calculate the time difference between the current time and the flight time
    time_difference = flight_time - current_time

    # Check if the time difference is less than the specified number of days
    return time_difference <= timedelta(days=num_days)


# Passagierfunktionen

@passagier_views.route('/buchung_suchen', methods=['GET', 'POST'])
@login_required
def buchung_suchen():
    input_buchungsnummer = request.args.get('buchungsnummer')

    buchung = Buchung.query.filter(Buchung.buchungsnummer == input_buchungsnummer). \
        order_by(Buchung.buchungsid.desc()).first()

    # für den ersten aufruf falls. Da keine Buchungsnummer eingegeben wird kann keine gefunden werden (sonst fehlermeldung)

    if buchung is None:

        # hier wird gesucht ob es buchungen zu dem angemeldeteten account gibt und die oberste angezeigt

        buchung = Buchung.query.filter(Buchung.nutzerid == current_user.id).order_by(Buchung.buchungsid.desc()).first()

        if buchung is None:
            flash('Kein Buchungen gefunden', category='error')
            return render_template('Passagier/buchung_suchen.html', user=current_user)

        else:
            ankunft_flughafen = Flughafen.query.filter(Buchung.flugid == Flug.flugid).where(
                Flug.abflugid == Flughafen.flughafenid).where(Buchung.buchungsnummer == buchung.buchungsnummer).first()
            # Kennung des Zielflughafens
            ziel_flughafen = Flughafen.query.filter(Buchung.flugid == Flug.flugid).where(
                Flug.zielid == Flughafen.flughafenid).where(Buchung.buchungsnummer == buchung.buchungsnummer).first()
            nutzer = Nutzerkonto.query.filter(
                Buchung.nutzerid == Nutzerkonto.id).where(Buchung.buchungsid == buchung.buchungsnummer).first()
            passagier = Passagier.query.filter(Buchung.buchungsnummer == buchung.buchungsnummer).where(
                Buchung.buchungsid == Passagier.buchungsid).all()
            flug = Flug.query.filter(Flug.flugid == Buchung.flugid).where(
                Buchung.buchungsnummer == buchung.buchungsnummer).first()
            flugzeug = Flugzeug.query.filter(Flugzeug.flugzeugid == flug.flugid).first()

            storno_possbile = True
            for i in passagier:
                if i.passagierstatus == "eingecheckt" or i.passagierstatus == "boarded":
                    storno_possbile = False

            check_in_available = is_flight_within_days(flug.sollabflugzeit, 1)

            if is_flight_within_days(flug.sollabflugzeit, 7):
                storno_text = "Ihr Flug ist in weniger als sieben Tagen. Wenn Sie Ihre Buchung jetzt stornieren, " \
                              "erhalten Sie keine Rückerstattung"

            elif is_flight_within_days(flug.sollabflugzeit, 14):
                storno_text = "Das Abflugdatum ihres Fluges ist zwischen 14 und 7 Tagen.Wenn Sie jetzt stornieren, " \
                              "wird Ihnen 50% des Buchungspreis zurückerstattet"

            else:
                storno_text = "Ihr Flug ist noch mehr als zwei Wochen entfernt. Ihnen wird der volle Buchungspreis " \
                              "zurückerstattet"

            return render_template('Passagier/buchung_suchen.html', buchung=buchung,
                                   ankunft_flughafen=ankunft_flughafen,
                                   ziel_flughafen=ziel_flughafen, flug=flug, user=current_user, nutzer=nutzer,
                                   check_in_available=check_in_available,
                                   passagier=passagier, storno_text=storno_text, storno_possbile=storno_possbile
                                   )

    # hier kann speziell nach nummer gesucht werden (muss aber mit nutzer id des angemedletetn nutzer
    # zusammenhängen)

    elif buchung.nutzerid == current_user.id:

        # Kennung des Ankunftflughafens
        ankunft_flughafen = Flughafen.query.filter(Buchung.flugid == Flug.flugid).where(
            Flug.abflugid == Flughafen.flughafenid).where(Buchung.buchungsnummer == input_buchungsnummer).first()
        # Kennung des Zielflughafens
        ziel_flughafen = Flughafen.query.filter(Buchung.flugid == Flug.flugid).where(
            Flug.zielid == Flughafen.flughafenid).where(Buchung.buchungsnummer == input_buchungsnummer).first()
        nutzer = Nutzerkonto.query.filter(
            Buchung.nutzerid == Nutzerkonto.id).where(Buchung.buchungsid == input_buchungsnummer).first()
        passagier = Passagier.query.filter(Buchung.buchungsnummer == input_buchungsnummer).where(
            Buchung.buchungsid == Passagier.buchungsid).all()
        flug = Flug.query.filter(Flug.flugid == Buchung.flugid).where(
            Buchung.buchungsnummer == input_buchungsnummer).first()
        check_in_available = is_flight_within_days(flug.sollabflugzeit, 1)

        # check if passagier is schon eingecheckt oder boarded

        storno_possbile = True
        for i in passagier:
            if i.passagierstatus == "eingecheckt" or i.passagierstatus == "boarded":
                storno_possbile = False

        # check wie weit weg der abflugzeitpunkt ist

        if is_flight_within_days(flug.sollabflugzeit, 7):
            storno_text = "Ihr Flug ist in weniger als sieben Tagen. Wenn Sie Ihre Buchung jetzt stornieren, " \
                          "erhalten Sie keine Rückerstattung"

        elif is_flight_within_days(flug.sollabflugzeit, 14):
            storno_text = "Das Abflugdatum ihres Fluges ist zwischen 14 und 7 Tagen.Wenn Sie jetzt stornieren, " \
                          "wird Ihnen 50% des Buchungspreis zurückerstattet"

        else:
            storno_text = "Ihr Flug ist noch mehr als zwei Wochen entfernt. Ihnen wird der volle Buchungspreis zurücker" \
                          "stattet"

        return render_template('Passagier/buchung_suchen.html', buchung=buchung, ankunft_flughafen=ankunft_flughafen,
                               ziel_flughafen=ziel_flughafen, flug=flug, user=current_user, nutzer=nutzer,
                               passagier=passagier, check_in_available=check_in_available, storno_text=storno_text,
                               storno_possbile=storno_possbile)
    else:
        flash('Kein Buchungen gefunden', category='error')
        return render_template('Passagier/buchung_suchen.html', user=current_user)


@passagier_views.route('/<stor_buchungsnummer>', methods=['GET', 'POST'])
def storno(stor_buchungsnummer):
    buchung = Buchung.query.filter(Buchung.buchungsnummer == stor_buchungsnummer).first()
    if buchung is not None:
        buchung.buchungsstatus = "storniert"
        db.session.commit()
        flash('Buchung erfolgreich storniert', category='success')

        buchungsnummer = buchung.buchungsnummer
        rechnungsnummer = Rechnung.query.where(Rechnung.buchungsid == buchung.buchungsid).first().rechnungsnummer

        return render_template("Passagier/stornierungsbestaetigung.html", user=current_user,
                               rechnungsnummer=rechnungsnummer, buchungsnummer=buchungsnummer)

    else:
        return redirect(url_for('passagier_views.buchung_suchen'))


@passagier_views.route('/gepaecksbestimmungen', methods=['GET'])
def gepaecksbestimmungen_anzeigen():
    return render_template("Passagier/gepaecksbestimmungen.html", user=current_user)