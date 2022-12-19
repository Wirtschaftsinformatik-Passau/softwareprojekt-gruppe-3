from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from select import select
from sqlalchemy import and_, select


from .models import Flug, Flughafen, Flugzeug, Buchung
from . import db

passagier_views = Blueprint('passagier_views', __name__)

@passagier_views.route('/flugstatus_erhalten', methods=['POST', 'GET'])
def flugstatus_erhalten():
    # Status von der Flugnummer holen, die eingetippt worden ist

    flug_nummer = request.form.get('flug_nummer')
    #gibt SQL Statement zurück
    #flugstatus = select(Flug.flugstatus).filter(flug_nummer == Flug.flugid)
    #gibt leere Brackets zurück
    flugstatus = Flug.query.filter(flug_nummer).all()

    return render_template("Passagier/flugstatus_erhalten.html", flugstatus=flugstatus)

@passagier_views.route('/online_check_in', methods=['POST', 'GET'])
def online_check_in():
    return render_template("Passagier/online_check_in.html")


@passagier_views.route('/buchung_suchen', methods=['GET'])
def buchungsuebersicht_erhalten():
    if request.method == "GET":
        buchung = Buchung.query.all()  # nummer und status werden gezeigt
        #von = select(Flughafen.stadt).filter(Flug.abflugid == Flughafen.flughafenid and Flug.flugid == Buchung.flugid)
        #nach = select(Flughafen.stadt).filter(Flug.zielid == Flughafen.flughafenid and Flug.flugid == Buchung.flugid)
        #datum = select(Flug.sollabflugzeit).filter(Flug.flugid == Buchung.flugid)
        von = select([Flughafen.stadt]).where(
            and_(Flug.abflugid == Flughafen.flughafenid, Flug.flugid == Buchung.flugid))


    return render_template("Passagier/buchung_suchen.html", buchung=buchung, von=von)