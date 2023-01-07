from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import current_user, login_required
from werkzeug.security import generate_password_hash
from . import db
from .models import Flug, Flughafen, Flugzeug, Nutzerkonto, Buchung, Passagier, Gepaeck
from sqlalchemy import or_, cast, Date

# store the standard routes for a website where the user can navigate to
passagier_views = Blueprint('passagier_views', __name__)

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
        Buchung.id == Nutzerkonto.id).where(Buchung.buchungsnummer == 999)
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
