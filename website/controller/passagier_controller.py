import random
import string

from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import current_user, login_required
from flask_mail import Message
from website import mail
from website import db
from website.model.models import Flug, Flughafen, Flugzeug, Nutzerkonto, Buchung, Passagier, Gepaeck, Rechnung
from datetime import date, datetime, timedelta
from reportlab.lib.pagesizes import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
import qrcode
import os

# store the standard routes for a website where the user can navigate to
passagier_views = Blueprint('passagier_views', __name__)

MINDESTLÄNGE_AUSWEISNUMMER = 9
EINE_WOCHE = 7
ZWEI_WOCHEN = 14


# Diese Hilfsfunktion generiert eine zufällige Boardingpassnummer
def generate_boarding_pass_number():
    boarding_pass_number = ''.join(random.choices(string.ascii_letters + string.digits, k=15))
    return boarding_pass_number


# Diese Hilfsfunktion generiert eine zufällige Buchungsnummer
def id_generator(size=8, chars=string.ascii_uppercase):
    return ''.join(random.choice(chars) for _ in range(size))


# Diese Hilfsfunktion prüft, ob das eingegebene Datum in der Vergangenheit liegt
def is_date_in_past(date):
    # Convert the input date to a datetime object
    date = datetime.strptime(date, '%Y-%m-%d')

    # Get the current date and time
    now = datetime.now()

    # Compare the input date to the current date and time
    if date < now:
        return True
    else:
        return False


# /F310/
# Diese Funktion erlaubt es einem Passagier, einen Flug zu buchen.
@passagier_views.route('/flug-buchen/<int:id>/<int:anzahlPassagiere>', methods=['GET', 'POST'])
@login_required
def flug_buchen(id, anzahlPassagiere):
    flughafen_liste = Flughafen.query.all()
    flug_data = Flug.query.filter_by(flugid=id).first()
    passagier_anzahl = 0
    buchung_preis = flug_data.preis * anzahlPassagiere

    if request.method == 'POST':
        # check ob nicht annulliert
        if flug_data.flugstatus == 'annuliert':
            flash('Der Flug wurde annuliert, bitte wählen Sie ein alternatives Datum.')
            return redirect(url_for('nutzer_ohne_account_views.home'))

        # check if still available seats

        anzahl_geb_passagiere = Passagier.query.join(Buchung). \
            filter(Buchung.flugid == flug_data.flugid).filter(Passagier.buchungsid == Buchung.buchungsid). \
            filter(Buchung.buchungsstatus != 'storniert').count()
        flugzeug_kapa = Flugzeug.query.get(flug_data.flugzeugid).anzahlsitzplaetze

        if (int(anzahl_geb_passagiere) + int(anzahlPassagiere)) > int(flugzeug_kapa):
            flash('Der Flug ist leider ausgebucht.', category='error')
            return redirect(url_for('nutzer_ohne_account_views.home'))

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

                if not is_date_in_past(passagier_data[2]):
                    flash('Das Geburtsdatum von ' + passagier_data[0] + ' ' + passagier_data[
                        1] + ' muss in der Vergangenheit liegen', category='error')

                    return render_template("Passagier/flug_buchen.html", user=current_user, flugid=id,
                                           anzahlPassagiere=anzahlPassagiere, preis=buchung_preis)

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


# Diese Hilfsfunktion erstellt eine Datei, in der alle Buchungsinformationen der Buchung zusammengefasst werden.
# Diese werden per Mail an Passagiere versendet.
@login_required
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

    msg = Message('Buchungsbestaetigung', sender='mailhog_grup3', recipients=[emailadresse])
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


# /F320/
# Diese Funktion erlaubt es einem Passagier, eine Buchung zu suchen.
@passagier_views.route('/buchung_suchen', methods=['GET', 'POST'])
def buchung_suchen():
    # Der Nutzer wird zur Login-Seite weitergeleitet, falls er noch nicht angemeldet ist
    if not current_user.is_authenticated:
        flash('Sie müssen angemeldet sein, um nach einer Buchung zu suchen')  # erscheint nicht
        return redirect(url_for('nutzer_mit_account_views.anmelden'))

    input_buchungsnummer = request.args.get('buchungsnummer')

    buchung = Buchung.query.join(Flug).filter(Buchung.buchungsnummer == input_buchungsnummer). \
        filter(Buchung.nutzerid == current_user.id). \
        order_by(Buchung.buchungsid.desc()).first()

    # für den ersten aufruf, falls keine Buchungsnummer eingegeben wird kann keine gefunden werden
    # (sonst fehlermeldung)

    if buchung is None:

        return render_template('Passagier/buchung_suchen.html', user=current_user)


    # speziell nach nummer gesucht werden (muss aber mit nutzer id des angemedletetn nutzer
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
        check_in_available = is_flight_within_days(flug.istabflugzeit, 1) and flug.istabflugzeit > datetime.now()
        gepaeckanzahl = db.session.query(Passagier, Buchung, Gepaeck).join(Buchung,
                                                                           Buchung.buchungsid == Passagier.buchungsid). \
            join(Gepaeck, Gepaeck.passagierid == Passagier.passagierid).filter(
            Buchung.buchungsid == buchung.buchungsid).count()

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
                               storno_possbile=storno_possbile, gepaeckanzahl=gepaeckanzahl)
    else:
        flash('Kein Buchungen gefunden', category='error')
        return render_template('Passagier/buchung_suchen.html', user=current_user)


# /F330/
# Diese Funktion erlaubt es einem Passagier, sich und Mitreisende online einzuchecken.
@passagier_views.route('/online_check_in', methods=['POST', 'GET'])
def online_check_in():
    # Übergabe jener Variablen aus der Buchung_suchen Funktion.
    # Abhängig von dem Button auf den geklickt wird, wird der eine oder andere Passagier ausgesucht
    buchungsnummer = request.args.get('buchungsnummer')
    vorname = request.args.get('vorname')
    nachname = request.args.get('nachname')
    buchungsid = request.args.get('buchungsid')
    emailadresse = Nutzerkonto.query.get_or_404(current_user.id).emailadresse

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
        passagier.staatsbuergerschaft = request.form['staatsangehoerigkeit']
        passagier.boardingpassnummer = generate_boarding_pass_number()
        passagier.passagierstatus = "eingecheckt"

        if not len(passagier.ausweisnummer) >= MINDESTLÄNGE_AUSWEISNUMMER:
            flash('Bitte überprüfen Sie die Ausweisnummer', category='error')
            return redirect(url_for('passagier_views.buchung_suchen'))

        db.session.commit()

        flash("Der Online-Check-In war erfolgreich! Ihre Boardingkarte können Sie im Anhang einsehen.")

        msg = Message('Boarding Pass', sender='mailhog_grup3', recipients=[emailadresse])
        msg.html = render_template("Passagier/online_check_in_email.html", user=current_user)
        msg.attach("boardingkarte.pdf", "application/pdf", boarding_karte(passagier.passagierid))
        mail.send(msg)

        return redirect(url_for('passagier_views.buchung_suchen', buchungsnummer=buchungsnummer))

    return render_template("Passagier/online_check_in.html", user=current_user, passagier=passagier, vorname=vorname,
                           nachname=nachname)


# Eingabe: Flugzeit, Anzahl an Tagen
# Diese Hilfsfunktion prüft, wie viele Tage die aktuelle Zeit von der übergebenen Flugzeit entfernt ist.
def is_flight_within_days(flight_time, num_days):
    # Get the current time
    current_time = datetime.now()

    # Calculate the time difference between the current time and the flight time
    time_difference = flight_time - current_time

    # Check if the time difference is less than the specified number of days
    return time_difference <= timedelta(days=num_days)


# /F340/
# Diese Funktion erlaubt es einem Passagier, eine Buchung zu stornieren.
@passagier_views.route('/<stor_buchungsnummer>', methods=['GET', 'POST'])
def storno(stor_buchungsnummer):
    buchung = Buchung.query.filter(Buchung.buchungsnummer == stor_buchungsnummer).first()
    if buchung is not None:
        buchung.buchungsstatus = "storniert"
        db.session.commit()
        flash('Buchung erfolgreich storniert', category='success')

        buchungsnummer = buchung.buchungsnummer
        rechnungsnummer = Rechnung.query.where(Rechnung.buchungsid == buchung.buchungsid).first().rechnungsnummer

        return redirect(url_for('passagier_views.stornierungsbestaetigung', user=current_user,
                                rechnungsnummer=rechnungsnummer, buchungsnummer=buchungsnummer,
                                buchungsid=buchung.buchungsid))

    else:
        return redirect(url_for('passagier_views.buchung_suchen', buchungsnummer=stor_buchungsnummer))


# Diese Hilfsfunktion sendet nach einer Storniernung eine Stornierungsbestätigung per Mail an den Ex-Passagier
@passagier_views.route('/stornierungsbestaetigung', methods=['POST', 'GET'])
def stornierungsbestaetigung():
    rechnungsnummer = request.args['rechnungsnummer']
    buchungsnummer = request.args['buchungsnummer']
    buchungsid = int(request.args['buchungsid'])

    emailadresse = Nutzerkonto.query.get_or_404(current_user.id).emailadresse
    flug = Flug.query.filter(Flug.flugid == Buchung.flugid).where(
        Buchung.buchungsnummer == buchungsnummer).first()

    msg = Message('Stornierungsbestaetigung', sender='mailhog_grup3', recipients=[emailadresse])
    msg.html = render_template("Passagier/stornierungsbestaetigung_email.html", user=current_user,
                               rechnungsnummer=rechnungsnummer, buchungsnummer=buchungsnummer, flug=flug)

    mail.send(msg)

    return render_template("Passagier/stornierungsbestaetigung.html", user=current_user,
                           rechnungsnummer=rechnungsnummer, buchungsnummer=buchungsnummer)


# Diese Hilfsfunktion dient dazu, die Gepäcksbestimmungen bei der Buchung anzuzeigen
@passagier_views.route('/gepaecksbestimmungen', methods=['GET'])
def gepaecksbestimmungen_anzeigen():
    return render_template("Passagier/gepaecksbestimmungen.html", user=current_user)


# Diese Hilfsfunktion erstellt basierend auf dem Online Check In eine Boardingkarte.
def boarding_karte(passagier_id):
    passagier = Passagier.query.filter(Passagier.passagierid == passagier_id).first()
    flug = Flug.query.join(Buchung, Buchung.flugid == Flug.flugid).join(Passagier,
                                                                        Passagier.buchungsid == Buchung.buchungsid).filter(
        Passagier.passagierid == passagier_id).first()

    # Kennung des Ankunftflughafens
    ankunft_flughafen = Flughafen.query.filter_by(flughafenid=flug.abflugid).first()
    # Kennung des Zielflughafens
    ziel_flughafen = Flughafen.query.filter_by(flughafenid=flug.zielid).first()

    # QR Code generieren
    qr_code = qrcode.make(passagier.boardingpassnummer)
    qr_code_path = os.path.join(os.path.abspath(""),
                                "boarding_pass_{}_{}.png".format(passagier.vorname, passagier.nachname))
    qr_code.save(qr_code_path)

    try:
        path = os.path.abspath("boarding_pass.pdf")
        doc = SimpleDocTemplate(path, pagesize=(5 * inch, 5 * inch))
        styles = getSampleStyleSheet()

        elements = []

        # Add passenger information & QR Image
        elements.append(Paragraph("<i >AirPassau</i>", styles["Heading4"]))
        elements.append(Paragraph("<b>Boarding Pass</b>", styles["Heading2"]))
        elements.append(Spacer(1, 5))
        elements.append(Image(qr_code_path, width=1 * inch, height=1 * inch))
        elements.append(Spacer(1, 1))
        elements.append(
            Paragraph(" Passagiername: {} {} ".format(passagier.vorname, passagier.nachname), styles["Normal"]))
        elements.append(Spacer(1, 1))
        elements.append(Paragraph("Von: {}".format(ankunft_flughafen.kennung), styles["Normal"]))
        elements.append(Spacer(1, 1))
        elements.append(Paragraph("Nach: {}".format(ziel_flughafen.kennung), styles["Normal"]))
        elements.append(Spacer(1, 1))
        elements.append(Paragraph("Fluglinie: {}".format(flug.flugnummer), styles["Normal"]))
        elements.append(Spacer(1, 1))
        elements.append(Paragraph("Sollabflugzeit: {}".format(flug.sollabflugzeit.time()), styles["Normal"]))
        elements.append(Spacer(1, 1))
        elements.append(Paragraph("Datum: {}".format(flug.sollabflugzeit.date()), styles["Normal"]))
        doc.build(elements)

    finally:
        os.remove(qr_code_path)
    # Return the generated PDF file

    with open(os.path.abspath("boarding_pass.pdf"), 'rb') as pdf:
        pdf_data = pdf.read()
        return pdf_data
