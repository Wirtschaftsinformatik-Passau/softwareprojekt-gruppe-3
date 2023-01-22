from flask import Blueprint, render_template, request, flash, redirect,Response, url_for
from flask_login import current_user, login_required
from . import db
from .models import Flug, Flughafen, Flugzeug, Nutzerkonto, Buchung, Passagier, Gepaeck
from datetime import datetime
import random, string
from reportlab.lib.pagesizes import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer,Image
from reportlab.lib.styles import getSampleStyleSheet
import qrcode
import os



# store the standard routes for a website where the user can navigate to
bodenpersonal_views = Blueprint('bodenpersonal_views', __name__)


def generate_boarding_pass_number():
    boarding_pass_number = ''.join(random.choices(string.ascii_letters + string.digits, k=15))
    return boarding_pass_number



def Kombination_1(buchungsnummer_1, vorname, nachname):
    buchung_1 = Buchung.query.filter(Buchung.buchungsnummer == buchungsnummer_1).all()

    # Kennung des Ankunftflughafens
    ankunft_flughafen = Flughafen.query.join(Flug, Flug.abflugid == Flughafen.flughafenid).join(
        Buchung, Buchung.flugid == Flug.flugid).filter(
        Buchung.buchungsnummer == buchungsnummer_1).all()

    # Kennung des Zielflughafens
    ziel_flughafen = Flughafen.query.join(Flug, Flug.zielid == Flughafen.flughafenid).join(
        Buchung, Buchung.flugid == Flug.flugid).filter(
        Buchung.buchungsnummer == buchungsnummer_1).all()

    flug = Flug.query.join(Buchung, Flug.flugid == Buchung.flugid).filter(
        Buchung.buchungsnummer == buchungsnummer_1).all()

    gepaeck = Gepaeck.query.join(Passagier, Gepaeck.passagierid == Passagier.passagierid).join(
        Buchung, Passagier.buchungsid == Buchung.buchungsid).join(Flug, Buchung.flugid == Flug.flugid).filter(
        Passagier.vorname == vorname,
        Passagier.nachname == nachname,
        Buchung.buchungsnummer == buchungsnummer_1).all()

    passagiere = Passagier.query.join(Buchung, Buchung.buchungsid == Passagier.buchungsid).filter(
        Buchung.buchungsnummer == buchungsnummer_1,
        Passagier.vorname == vorname,
        Passagier.nachname == nachname).all()

    return buchung_1, ankunft_flughafen, ziel_flughafen, flug, gepaeck, passagiere


def Kombination_2(buchungsnummer_2, ausweisnummer):
    passagiere = Passagier.query.join(Buchung, Buchung.buchungsid == Passagier.buchungsid).filter(
        Buchung.buchungsnummer == buchungsnummer_2,
        Passagier.ausweisnummer == ausweisnummer).all()

    buchung_2 = Buchung.query.filter(Buchung.buchungsnummer == buchungsnummer_2).all()

    # Kennung des Ankunftflughafens
    ankunft_flughafen = Flughafen.query.join(Flug, Flug.abflugid == Flughafen.flughafenid).join(
        Buchung, Buchung.flugid == Flug.flugid).filter(
        Buchung.buchungsnummer == buchungsnummer_2).all()

    # Kennung des Zielflughafens
    ziel_flughafen = Flughafen.query.join(Flug, Flug.zielid == Flughafen.flughafenid).join(
        Buchung, Buchung.flugid == Flug.flugid).filter(
        Buchung.buchungsnummer == buchungsnummer_2).all()

    flug = Flug.query.join(Buchung, Flug.flugid == Buchung.flugid).filter(
        Buchung.buchungsnummer == buchungsnummer_2).all()

    gepaeck = Gepaeck.query.join(Passagier, Gepaeck.passagierid == Passagier.passagierid).join(
        Buchung, Passagier.buchungsid == Buchung.buchungsid).join(
        Flug, Buchung.flugid == Flug.flugid).filter(
        Passagier.ausweisnummer == ausweisnummer, Buchung.buchungsnummer == buchungsnummer_2).all()

    return passagiere, buchung_2, ankunft_flughafen, ziel_flughafen, flug, gepaeck


# Diese Funktion stellt die Starseite des Bodenpersonals & die passagier_suchen Funktion dar
@bodenpersonal_views.route('/home_bp', methods=["GET", "POST"])
def home():
    today = datetime.now().date()
    if request.method == 'POST':
        buchungsnummer_1 = request.form.get('buchungsnummer_1')
        buchungsnummer_2 = request.form.get('buchungsnummer_2')
        vorname = request.form.get('vorname')
        nachname = request.form.get('nachname')
        ausweisnummer = request.form.get('ausweisnummer')

        if ((buchungsnummer_1 and vorname and nachname) or (buchungsnummer_2 and ausweisnummer)):

            if buchungsnummer_1 and vorname and nachname:
                buchung_1, ankunft_flughafen, ziel_flughafen, flug, gepaeck, passagiere = Kombination_1(
                    buchungsnummer_1,
                    vorname, nachname)
                for flug_row in flug:
                    flug_datum = flug_row.sollabflugzeit.date()

                return render_template("bodenpersonal/home_bp.html", buchung_1=buchung_1,
                                       ankunft_flughafen=ankunft_flughafen,
                                       ziel_flughafen=ziel_flughafen, flug=flug, user=current_user,
                                       passagiere=passagiere, gepaeck=gepaeck, today=today, flug_datum=flug_datum)

            elif buchungsnummer_2 and ausweisnummer:
                passagiere, buchung_2, ankunft_flughafen, ziel_flughafen, flug, gepaeck = Kombination_2(
                    buchungsnummer_2, ausweisnummer)
                for flug_row in flug:
                    flug_datum = flug_row.sollabflugzeit.date()
                return render_template("bodenpersonal/home_bp.html", buchung_2=buchung_2,
                                       ankunft_flughafen=ankunft_flughafen,
                                       ziel_flughafen=ziel_flughafen, flug=flug, user=current_user,
                                       passagiere=passagiere, gepaeck=gepaeck, today=today, flug_datum=flug_datum)
        else:
            flash("Entweder müssen die Felder Buchungsnummer, Vorname und Nachname oder die Felder"
                  " Buchungsnummer und Ausweisnummer  ausgefüllt werden.", category="error")
            return render_template("bodenpersonal/home_bp.html")

    else:
        return render_template("bodenpersonal/home_bp.html")






@bodenpersonal_views.route('/einchecken', methods=['POST', 'GET'])
def einchecken():
    buchungsnummer = request.args.get('buchungsnummer_1')
    vorname = request.args.get('vorname')
    nachname = request.args.get('nachname')
    buchungsid = request.args.get('buchungsid')

    passagier = Passagier.query.filter(Passagier.buchungsid == buchungsid).where(Passagier.vorname == vorname). \
        where(Passagier.nachname == nachname).first()
    if request.method == 'POST':
        passagier.nachname = nachname
        passagier.vorname = vorname
        passagier.ausweistyp = request.form['ausweistyp']
        passagier.ausweisnummer = request.form['ausweissnummer']
        passagier.ausweisgueltigkeit = request.form['ausweisgueltigkeit']
        passagier.staatsbuergerschaft = request.form['staatsangehoerigkeit']
        passagier.passagierstatus = "eingecheckt"
        passagier.boardingpassnummer = generate_boarding_pass_number()
        db.session.add(passagier)
        db.session.commit()

        flash("Check-In erfolgreich")
        return redirect(url_for('bodenpersonal_views.home'))

    return render_template('bodenpersonal/einchecken.html', user=current_user, passagier=passagier, vorname=vorname,
                           nachname=nachname)

@bodenpersonal_views.route('/koffer_einchecken', methods=["POST"])
def koffer_einchecken():
    buchungsid = request.form.get('buchungsid')
    buchungsnummer = request.form.get('buchungsnummer')
    vorname = request.form.get('vorname')
    nachname = request.form.get('nachname')
    gepaeckid = request.form.getlist('gepaeckid')

    for id in gepaeckid:
        gepaeck = Gepaeck.query.filter(Gepaeck.gepaeckid == id).first()
        gepaeck.status = "Eingecheckt"
        db.session.commit()

    flash("Koffer erfolgreich eingecheckt!", category="success")
    return redirect(url_for('bodenpersonal_views.home', buchungsnummer=buchungsnummer, vorname=vorname, nachname=nachname))

@bodenpersonal_views.route('/koffer_label', methods=['POST'])
def koffer_label():
    passagier_id = request.args.get('passagier_id')
    gepaeckid = request.args.get('gepaeckid')

    passagier = Passagier.query.filter(Passagier.passagierid == passagier_id).first()
    flug = Flug.query.join(Buchung, Buchung.flugid == Flug.flugid).join(Passagier,Passagier.buchungsid == Buchung.buchungsid).filter(
        Passagier.passagierid == passagier_id).first()

    # Kennung des Ankunftflughafens
    ankunft_flughafen = Flughafen.query.join(Flug, Flug.abflugid == Flughafen.flughafenid).join(
        Buchung, Buchung.flugid == Flug.flugid).join(
        Passagier,Passagier.buchungsid == Buchung.buchungsid).join(
        Gepaeck,Gepaeck.passagierid ==passagier_id).filter(
        Gepaeck.gepaeckid == gepaeckid).first()

    # Kennung des Zielflughafens
    ziel_flughafen =  Flughafen.query.join(Flug, Flug.zielid == Flughafen.flughafenid).join(
        Buchung, Buchung.flugid == Flug.flugid).join(
        Passagier,Passagier.buchungsid == Buchung.buchungsid).join(
        Gepaeck,Gepaeck.passagierid ==passagier_id).filter(
        Gepaeck.gepaeckid == gepaeckid).first()
    try:
        doc = SimpleDocTemplate("koffer_label.pdf", pagesize=(5 * inch, 5 * inch))
        styles = getSampleStyleSheet()

        # QR Code generieren
        qr_code = qrcode.make(gepaeckid)
        qr_code_path = "koffer_label_{}_{}.png".format(passagier.vorname, passagier.nachname)
        qr_code.save(qr_code_path)

        elements = []

        # Add passenger information & QR Image
        elements.append(Paragraph("<b>Gepäcketikett</b>" , styles["Heading2"]))
        elements.append(Paragraph("<i>AirPassau</i>", styles["Heading4"]))
        elements.append(Spacer(1, 5))
        elements.append(Image(qr_code_path, width=1 * inch, height=1 * inch))
        elements.append(Spacer(1, 1))
        elements.append(Paragraph(" Passagiername: {} {} ".format(passagier.vorname , passagier.nachname), styles["Normal"]))
        elements.append(Spacer(1, 1))
        elements.append(Paragraph("Von: {}".format(ankunft_flughafen.kennung), styles["Normal"]))
        elements.append(Spacer(1, 1))
        elements.append(Paragraph("Nach: {}".format(ziel_flughafen.kennung), styles["Normal"]))
        elements.append(Spacer(1, 1))
        elements.append(Paragraph("Fluglinie: {}".format(flug.flugnummer), styles["Normal"]))
        doc.build(elements)

    finally:
        os.remove(qr_code_path)
    # Return the generated PDF file
    with open("koffer_label.pdf", 'rb') as pdf:
        pdf_data = pdf.read()
        response = Response(pdf_data, content_type='application/pdf', headers={
            "Content-Disposition": "attachment;filename=koffer_label_{}_{}.pdf".format(passagier.vorname,
                                                                                        passagier.nachname)})
        return response


@bodenpersonal_views.route('/boarding', methods=['POST'])
def boarding():
    buchungsid = request.args.get('buchungsid')
    vorname = request.args.get('vorname')
    nachname = request.args.get('nachname')
    passagier= Passagier.query.filter(Passagier.buchungsid == buchungsid).where(Passagier.vorname == vorname). \
        where(Passagier.nachname == nachname).first()
    passagier.passagierstatus = "Boarded"
    db.session.add(passagier)
    db.session.commit()
    flash("Passagier erfolgreich geboarded","success")
    return redirect(url_for('bodenpersonal_views.home',buchungsid=buchungsid, vorname=vorname, nachname=nachname))




@bodenpersonal_views.route('/generate_boarding_pass', methods=['POST'])
def generate_boarding_pass():

    passagier_id = request.args.get('passagier_id')
    passagier = Passagier.query.filter(Passagier.passagierid == passagier_id).first()
    flug=Flug.query.join(Buchung,Buchung.flugid == Flug.flugid).join(Passagier,
        Passagier.buchungsid == Buchung.buchungsid).filter(Passagier.passagierid == passagier_id).first()

    # Kennung des Ankunftflughafens
    ankunft_flughafen = Flughafen.query.join(Flug, Flug.abflugid == Flughafen.flughafenid).join(
        Buchung, Buchung.flugid == Flug.flugid).join(Passagier,
        Passagier.buchungsid == Buchung.buchungsid).filter(Passagier.passagierid == passagier_id).first()

    # Kennung des Zielflughafens
    ziel_flughafen = Flughafen.query.join(Flug, Flug.zielid == Flughafen.flughafenid).join(
        Buchung, Buchung.flugid == Flug.flugid).join(Passagier,
        Passagier.buchungsid == Buchung.buchungsid).filter(Passagier.passagierid == passagier_id).first()

    try:
        doc = SimpleDocTemplate("boarding_pass.pdf", pagesize=(5 * inch, 5 * inch))
        styles = getSampleStyleSheet()

        # QR Code generieren
        qr_code = qrcode.make(passagier.boardingpassnummer)
        qr_code_path = "boarding_pass_{}_{}.png".format(passagier.vorname, passagier.nachname)
        qr_code.save(qr_code_path)

        elements = []

        # Add passenger information & QR Image
        elements.append(Paragraph("<b>Boarding Pass</b>" , styles["Heading2"]))
        elements.append(Paragraph("<i>AirPassau</i>", styles["Heading4"]))
        elements.append(Spacer(1, 5))
        elements.append(Image(qr_code_path, width=1 * inch, height=1 * inch))
        elements.append(Spacer(1, 1))
        elements.append(Paragraph(" Passagiername: {} {} ".format(passagier.vorname , passagier.nachname), styles["Normal"]))
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
    with open("boarding_pass.pdf", 'rb') as pdf:
        pdf_data = pdf.read()
        response = Response(pdf_data, content_type='application/pdf', headers={
            "Content-Disposition": "attachment;filename=boarding_pass_{}_{}.pdf".format(passagier.vorname,
                                                                                        passagier.nachname)})
        return response

@bodenpersonal_views.route('/fluege_pruefen', methods=["GET", "POST"])
def fluege_pruefen():
    if request.method == 'POST':
        # get the flight number from the html form
        flugnummer = request.form['flugnummer']
        datum = request.form['datum']

        # query the database to get the flight with the specified flight number
        flug = Flug.query.filter_by(flugnummer=flugnummer, istabflugzeit=datum).first()
        # print(flug)
        if flug is None:
            flash("Zu Ihren Suchkriterien wurde kein passender Flug gefunden", "error")
        else:
            # get the bookings for the flight
            buchungen = Buchung.query.filter(Buchung.flugid == Flug.flugid).where(Flug.flugnummer == flugnummer).where(
                Flug.istabflugzeit == datum).all()

            # get the passenger info for each booking
            passagiere = []
            for buchung in buchungen:
                p = db.session.query(Buchung.buchungsnummer, Passagier.vorname, Passagier.nachname,
                                     Passagier.passagierstatus,Passagier.geburtsdatum).join(Passagier).filter(
                    Passagier.buchungsid == buchung.buchungsid).all()
                passagiere.extend(p)
            return render_template('bodenpersonal/fluege_pruefen.html', flugnummer=flugnummer, passagiere=passagiere,
                                   buchungen=buchungen)

    return render_template('bodenpersonal/fluege_pruefen.html')



