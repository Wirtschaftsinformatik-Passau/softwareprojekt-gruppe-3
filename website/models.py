from flask import Flask
from flask_mysqldb import MySQL
#import mysql.connector
from website import db, create_app


class Flugzeug(db.Model):
    flugzeugid = db.Column(db.Integer, primary_key=True)
    modell = db.Column(db.String(150), unique=False)
    hersteller = db.Column(db.String(150))
    anzahlsitzplaetze = db.Column(db.Integer)

    def __repr__(self):
        return "flugzeugid: {1} | modell: {1} | hersteller: {1} | anzahlsitzplaetze: {1}".format(
            self.flugzeugid, self.modell, self.hersteller, self.anzahlsitzplaetze)


class Nutzerkonto(db.Model):
    nutzerid = db.Column(db.Integer, primary_key=True)
    vorname = db.Column(db.String(150))
    nachname = db.Column(db.String(150))
    emailadresse = db.Column(db.String(150))
    gehashtespasswort = db.Column(db.String(150))
    rolle = db.Column(db.Enum("Bodenpersonal", "Verwaltungspersonal", "Passagier"))


class Flughafen (db.Model):
    flughafenid = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    kennung = db.Column(db.String(50))
    stadt = db.Column(db.String(150))
    land = db.Column(db.String(150))


class Flug (db.Model):
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
    gate = db.Column(db.String(50))

