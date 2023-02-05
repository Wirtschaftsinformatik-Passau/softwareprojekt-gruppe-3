from flask import Blueprint, jsonify, request,url_for
from website.model.models import Flug, Flughafen
from datetime import datetime

flight_api = Blueprint('flight_api', __name__)


@flight_api.route('/flights', methods=['GET'])
def get_flights():
    von = request.args.get('von')
    nach = request.args.get('nach')
    datum = request.args.get('datum')
    anzahl_passagier=request.args.get('anzahl_passagier')

    # Kennung des Ankunftflughafens
    ankunft_flughafen = Flughafen.query.filter_by(Flughafen.kennung == von).first()
    # Kennung des Zielflughafens
    ziel_flughafen = Flughafen.query.filter_by(Flughafen.kennung == nach).first()

    if not ziel_flughafen:
        return jsonify(
            {'error': 'Der Flughafen {} wird von uns leider nicht angeflogen'.format(nach)}), 400

    if not anzahl_passagier or anzahl_passagier <= 0:
        return jsonify({'error': 'Die Anzahl der Passagiere muss kann nicht null sein.'}), 400

    if not von or not nach or not datum or not anzahl_passagier:
        return jsonify({'error': 'fehlende Parameter'}), 400

    datum = datetime.strptime(datum, '%Y-%m-%d')
    today = datetime.now().date()

    if datum < today:
        return jsonify({'error': 'Bitte geben Sie ein Datum ein, welches in der Zukunft liegt.'}), 400

    flug = Flug.query.filter(Flug.abflugid == ankunft_flughafen.flughafenid,
                      Flug.zielid == ziel_flughafen.flughafenid,
                      Flug.sollabflugzeit.date() == datum).first()
    if not flug:
        return jsonify({'error': 'Der Flug existiert nicht.'}), 404

    results = []
    results.append({
        'FlugID': flug.flugid,
        'Preis': flug.preis,
        'Abflugzeit': flug.sollabflugzeit,
        'Ankunftszeit': flug.sollankunftszeit,
        'Buchungslink': url_for('passagier_controller.flug_buchen', id=flug.flugid, anzahlPassagiere=anzahl_passagier)
        })

    return jsonify({'results': results})










