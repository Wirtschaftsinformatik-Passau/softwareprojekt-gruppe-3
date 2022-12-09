from flask import Flask
from flask_mysqldb import MySQL
import mysql.connector
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
    rolle = db.Enum("Bodenpersonal", "Verwaltungspersonal", "Passagier")
