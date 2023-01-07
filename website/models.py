# from flask import Flask
# from flask_mysqldb import MySQL
# import mysql.connector
from flask_login import UserMixin

from website import db, create_app


class Nutzerkonto(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    vorname = db.Column(db.String(150))
    nachname = db.Column(db.String(150))
    emailadresse = db.Column(db.String(150), unique=True)
    passwort = db.Column(db.String(255))
    rolle = db.Column(db.Enum("Bodenpersonal", "Verwaltungspersonal", "Passagier"))


class Buchung(db.Model):
    buchungsid = db.Column(db.Integer, primary_key=True)
    id = db.Column(db.Integer, db.ForeignKey('nutzerkonto.id'))
    flugid = db.Column(db.Integer, db.ForeignKey('flug.flugid'))
    buchungsnummer = db.Column(db.String(50))
    buchungsstatus = db.Column(db.Enum("gebucht", "storniert", "verfallen"))


class Flugzeug(db.Model):
    flugzeugid = db.Column(db.Integer, primary_key=True)
    modell = db.Column(db.String(150), unique=False)
    hersteller = db.Column(db.String(150))
    anzahlsitzplaetze = db.Column(db.Integer)
    status = db.Column(db.Enum('aktiv', 'inaktiv'), default='aktiv')

    def __repr__(self):
        return "flugzeugid: {1} | modell: {1} | hersteller: {1} | anzahlsitzplaetze: {1}".format(
            self.flugzeugid, self.modell, self.hersteller, self.anzahlsitzplaetze)


class Flughafen(db.Model):
    flughafenid = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    kennung = db.Column(db.String(50))
    stadt = db.Column(db.String(150))
    land = db.Column(db.String(150))


class Flug(db.Model):
    flugid = db.Column(db.Integer, primary_key=True)
    flugzeugid = db.Column(db.Integer, db.ForeignKey('flugzeug.flugzeugid'))
    abflugid = db.Column(db.Integer, db.ForeignKey('flughafen.flughafenid'))
    zielid = db.Column(db.Integer, db.ForeignKey('flughafen.flughafenid'))
    flugstatus = db.Column(db.Enum("pünktlich", "annuliert", "verspätet"))
    istabflugzeit = db.Column(db.DateTime(timezone=True))
    istankunftszeit = db.Column(db.DateTime(timezone=True))
    sollabflugzeit = db.Column(db.DateTime(timezone=True))
    sollankunftszeit = db.Column(db.DateTime(timezone=True))
    flugnummer = db.Column(db.String(50))
    preis = db.Column(db.Integer)


class Gepaeck(db.Model):
    gepaeckid = db.Column(db.Integer, primary_key=True)
    passagierid = db.Column(db.Integer)
    gewicht = db.Column(db.Float)
    status = db.Column(db.Enum("gebucht", "storniert", "eingecheckt"))


class Passagier(db.Model):
    passagierid = db.Column(db.Integer, primary_key=True)
    buchungsid = db.Column(db.Integer, db.ForeignKey('buchung.buchungsid'))
    ausweistyp = db.Column(db.Enum("Ausweis", "Reisepass"))
    ausweisnummer = db.Column(db.String(10))
    ausweisgueltigkeit = db.Column(db.DateTime(timezone=True))
    vorname = db.Column(db.String(50))
    nachname = db.Column(db.String(50))
    geburtsdatum = db.Column(db.DateTime(timezone=True))
    staatsbuergerschaft = db.Column(db.String(30))
    boardingpassnummer = db.Column(db.String(50))
    passagierstatus = db.Column(db.Enum("gebucht", "eingecheckt", "boarded"))


class Rechnung(db.Model):
    rechnungsid = db.Column(db.Integer, primary_key=True)
    buchungsid = db.Column(db.Integer, db.ForeignKey('buchung.buchungsid'))
    status = db.Column(db.Enum("zurückerstattet", "bezahlt"))
    rechnungsnummer = db.Column(db.Integer)
    rechnungsinhalt = db.Column(db.String(500))
    betrag = db.Column(db.Integer)
