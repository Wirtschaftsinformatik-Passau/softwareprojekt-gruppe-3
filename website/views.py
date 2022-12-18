from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from select import select
from sqlalchemy import and_, select


from .models import Flug, Flughafen, Flugzeug, Buchung
from . import db

# store the standard routes for a website where the user can navigate to
views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
def home():
    flughafen_liste = Flughafen.query.with_entities(Flughafen.stadt)

    vonID = Flughafen.query.filter(Flughafen.stadt == request.args.get('von')).with_entities(Flughafen.flughafenid)
    nachID = Flughafen.query.filter(Flughafen.stadt == request.args.get('nach')).with_entities(Flughafen.flughafenid)
    abflug = request.args.get('Abflugdatum')
    passagiere = request.args.get('AnzahlPersonen')

    print(vonID, nachID)

    #Datenbankabrag nach Abflug und Ziel Flughafen sowie Datum und Passagieranzahl < Summe bereits gebuchter Passagiere

    fluege = Flug.query.filter(Flug.abflugid == vonID, Flug.zielid == nachID)

    return render_template("Gast/home.html", fluege=fluege, flughafen_liste=flughafen_liste)

