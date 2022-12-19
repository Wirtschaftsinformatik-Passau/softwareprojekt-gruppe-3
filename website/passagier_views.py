from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from select import select
from sqlalchemy import and_, select
from .models import Flug, Flughafen, Buchung, Nutzerkonto, Gepaeck, Passagier
from . import db

passagier_views = Blueprint('passagier_views', __name__)


@passagier_views.route('/flugstatus_erhalten', methods=['POST', 'GET'])
def flugstatus_erhalten():
    # Status von der Flugnummer holen, die eingetippt worden ist

    flug_nummer = request.form.get('flug_nummer')
    # gibt SQL Statement zurück
    # flugstatus = select(Flug.flugstatus).filter(flug_nummer == Flug.flugid)
    # gibt leere Brackets zurück
    flugstatus = Flug.query.filter(flug_nummer).all()

    return render_template("Passagier/flugstatus_erhalten.html", flugstatus=flugstatus)


@passagier_views.route('/online_check_in', methods=['POST', 'GET'])
def online_check_in():
    return render_template("Passagier/online_check_in.html")


@passagier_views.route('/buchung_suchen', methods=['GET', 'POST'])
def buchung_suchen():
    input_buchungsnummer = request.form.get('buchungsnummer')

    buchung = Buchung.query.filter(Buchung.buchungsnummer == 999)
    #Kennung des Ankunftflughafens
    ankunft_flughafen = Flughafen.query.filter(Buchung.flugid == Flug.flugid).where(
        Flug.abflugid == Flughafen.flughafenid).where(Buchung.buchungsnummer == 999)
    #Kennung des Zielflughafens
    ziel_flughafen = Flughafen.query.filter(Buchung.flugid == Flug.flugid).where(
        Flug.zielid == Flughafen.flughafenid).where(Buchung.buchungsnummer == 999)
    nutzer = Nutzerkonto.query.filter(
        Buchung.nutzerid == Nutzerkonto.id).where(Buchung.buchungsnummer == 999)
    flug = Flug.query.filter(Flug.flugid == Buchung.flugid).where(Buchung.buchungsnummer == 999)
    gepaeck = Gepaeck.query.all()

    return render_template('Passagier/buchung_suchen.html', buchung=buchung, ankunft_flughafen=ankunft_flughafen,
                           ziel_flughafen=ziel_flughafen, flug=flug, nutzer=nutzer, gepaeck=gepaeck)
