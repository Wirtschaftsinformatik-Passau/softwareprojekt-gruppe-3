from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import current_user, login_required
from . import db
from .models import Flug, Flughafen, Flugzeug, Nutzerkonto, Buchung, Passagier, Gepaeck
from sqlalchemy.orm import aliased

Flughafen_alias = aliased(Flughafen, name='zielflughafen')


# store the standard routes for a website where the user can navigate to
bodenpersonal_views = Blueprint('bodenpersonal_views', __name__)

def Kombination_1(buchungsnummer_1,vorname,nachname):

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

    return buchung_1,ankunft_flughafen,ziel_flughafen,flug,gepaeck,passagiere

def Kombination_2(buchungsnummer_2,ausweisnummer):

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

    return passagiere,buchung_2,ankunft_flughafen,ziel_flughafen,flug,gepaeck



# Diese Funktion stellt die Starseite des Bodenpersonals & die passagier_suchen Funktion dar
@bodenpersonal_views.route('/home_bp',methods=["GET","POST"])
def home():
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

                return render_template("bodenpersonal/home_bp.html", buchung_1=buchung_1,
                                       ankunft_flughafen=ankunft_flughafen,
                                       ziel_flughafen=ziel_flughafen, flug=flug, user=current_user,
                                       passagiere=passagiere, gepaeck=gepaeck)

            elif buchungsnummer_2 and ausweisnummer :
                passagiere, buchung_2, ankunft_flughafen, ziel_flughafen, flug, gepaeck = Kombination_2(
                    buchungsnummer_2, ausweisnummer)
                return render_template("bodenpersonal/home_bp.html", buchung_2=buchung_2,
                                       ankunft_flughafen=ankunft_flughafen,
                                       ziel_flughafen=ziel_flughafen, flug=flug, user=current_user,
                                       passagiere=passagiere, gepaeck=gepaeck)
        else:
            flash("Entweder müssen die Felder Buchungsnummer, Vorname und Nachname oder die Felder"
                  " Buchungsnummer und Ausweisnummer  ausgefüllt werden.", category="error")
            return render_template("bodenpersonal/home_bp.html")

    else:
        return render_template("bodenpersonal/home_bp.html")










@bodenpersonal_views.route('/boarding', methods=['POST'])
def boarding():
    return render_template('bodenpersonal/boarding.html', user=current_user)

@bodenpersonal_views.route('/einchecken', methods=['POST', 'GET'])
def einchecken():
    buchungsnummer = request.args.get('buchungsnummer_1')
    vorname = request.args.get('vorname')
    nachname = request.args.get('nachname')
    buchungsid = request.args.get('buchungsid')


    passagier= Passagier.query.filter(Passagier.buchungsid == buchungsid).where(Passagier.vorname == vorname). \
        where(Passagier.nachname == nachname).first()
    #print(passagier.vorname)

    if request.method == 'POST':
        passagier.nachname = nachname
        passagier.vorname = vorname
        passagier.ausweistyp = request.form['ausweistyp']
        passagier.ausweisnummer = request.form['ausweissnummer']
        passagier.ausweisgueltigkeit = request.form['ausweisgueltigkeit']
        passagier.passagierstatus = "eingecheckt"
        db.session.add(passagier)
        db.session.commit()
        flash("Check-In erfolgreich")

        return redirect(url_for('bodenpersonal_views.home'))




    return render_template('bodenpersonal/einchecken.html', user=current_user, passagier=passagier, vorname=vorname,
                           nachname=nachname)

@bodenpersonal_views.route('/fluege_pruefen',methods=["GET","POST"])
def fluege_pruefen():
    if request.method == 'POST':
        # get the flight number from the html form
        flugnummer = request.form['flugnummer']

        # query the database to get the flight with the specified flight number
        flug = Flug.query.filter_by(flugnummer=flugnummer).first()
        if flug is None:
            flash("Kein Flug mit dieser Nummer ist gefunden","error")
        else:
            # get the bookings for the flight
            buchungen = Buchung.query.filter(Buchung.flugid == Flug.flugid).where(Flug.flugnummer == flugnummer).all()

            # get the passenger info for each booking
            passagiere = []
            for buchung in buchungen:
                p = db.session.query(Buchung.buchungsnummer, Passagier.vorname, Passagier.nachname,
                                     Passagier.passagierstatus).join(Passagier).filter(
                                     Passagier.buchungsid == buchung.buchungsid).all()
                passagiere.extend(p)
            return render_template('bodenpersonal/fluege_pruefen.html', flugnummer=flugnummer, passagiere=passagiere,buchungen=buchungen)

    return render_template('bodenpersonal/fluege_pruefen.html')







