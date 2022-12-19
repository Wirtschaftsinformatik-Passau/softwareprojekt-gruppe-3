from website import db
from flask_login import UserMixin


class Buchung(db.Model):
    buchungsid = db.Column(db.Integer, primary_key=True)
    nutzerid = db.Column(db.Integer, db.ForeignKey('nutzerkonto.id'))
    flugid = db.Column(db.Integer, db.ForeignKey('flug.flugid'))
    buchungsnummer = db.Column(db.Integer)
    buchungsstatus = db.Column(db.Enum("gebucht", "storniert", "verfallen"))


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
    gate = db.Column(db.String(50))


class Flughafen (db.Model):
    flughafenid = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    kennung = db.Column(db.String(50))
    stadt = db.Column(db.String(150))
    land = db.Column(db.String(150))


class Flugzeug(db.Model):
    flugzeugid = db.Column(db.Integer, primary_key=True)
    modell = db.Column(db.String(150), unique=False)
    hersteller = db.Column(db.String(150))
    anzahlsitzplaetze = db.Column(db.Integer)

    def __repr__(self):
        return "flugzeugid: {1} | modell: {1} | hersteller: {1} | anzahlsitzplaetze: {1}".format(
            self.flugzeugid, self.modell, self.hersteller, self.anzahlsitzplaetze)


class Gepaeck(db.Model):
    gepaeckid = db.Column(db.Integer, primary_key=True)
    passagierid = db.Column(db.Integer)
    gewicht = db.Column(db.Float)
    status = db.Column(db.Enum("gebucht", "storniert", "eingecheckt"))


class Nutzerkonto(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    vorname = db.Column(db.String(150))
    nachname = db.Column(db.String(150))
    emailadresse = db.Column(db.String(150), unique=True)
    passwort = db.Column(db.String(150))
    rolle = db.Column(db.Enum("Bodenpersonal", "Verwaltungspersonal", "Passagier"))


class Passagier (db.Model):
    passagierid = db.Column(db.Integer, primary_key=True)
    buchungsid = db.Column(db.Integer, db.ForeignKey('buchung.buchungsid'))
    ausweistyp = db.Column(db.Enum("Ausweis", "Reisepass"))
    ausweisnummer = db.Column(db.String(10))
    ausweisgueltigkeit = db.Column(db.DateTime(timezone=True))
    vorname = db.Column(db.String(50))
    nachname = db.Column(db.String(50))
    geburtsdatum = db.Column(db.DateTime(timezone=True))
    staatsbuergerschaft = db.Column(db.String(30))
    boardingpassnummer = db.Column(db.Integer)
    passagierstatus = db.Column(db.Enum("eingecheckt", "boarded"))


class Rechnung(db.Model):
    rechnungsid = db.Column(db.Integer, primary_key=True)
    buchungsid = db.Column(db.Integer)
    status = db.Column(db.Enum("zurückerstattet", "bezahlt"))
    rechnungsnummer = db.Column(db.Integer)
