# Airline

## Projektbeschreibung

### Projektziele

Ziel des Projekts ist die Erstellung eines Flugbuchungssystems für eine regionale Airline. Das Flugbuchungssystem soll alle unter "Funktionen" aufgeführte Funktionen beinhalten. Um die Funktionalität des Systems gewährleisten zu können, wurden die zu entwickelnden Funktionen unterschiedlichen Zielgruppen zugeordnet. Die Zielgruppen lauten "Nutzer ohne Account", "Preisvergleichsportal", "Nutzer mit Account", "Passagier", "Bodenpersonal" und "Verwaltungspersonal".

### Funktionen

Die Funktionen sind nach Zielgruppen geordnet. Da sich die Funktionen mancher Zielgruppen überschneiden, stehen diese in Beziehung zueinander. Folgende Zielgruppenbeziehungen existieren:

* "Preisvergleichsportal" extends "Nutzer ohne Account"
* "Passagier" extends "Nutzer ohne Account"
* "Passaier" extends "Nutzer mit Account"
* "Bodenpersonal" extends "Nutzer mit Account"
* "Verwaltungspersonal" extends "Nutzer mit Account"

Im Folgenden ist die Funktionsaufteilung nach Zielgruppen dargestellt.

* Nutzer ohne Account: Startseite anzeigen, Flug suchen, Flugstatus überprüfen, Fluglinien einsehen, Registrieren
* Preisverleichsportal: REST-API
* Nutzer mit Account: Einloggen, Passwort ändern, Passwort vergessen, Profil anzeigen
* Passagier: Flug buchen, Buchungen suchen, Online-Check-In, Buchung stornieren
* Bodenpersonal: Startseite des Bodenpersonals anzeigen, Passagier suchen, Check-In, Auslastung der Flüge prüfen
* Verwaltungspersonal: Startseite (Verwaltung) anzeigen, Flugzeuge anlegen, Flugzeuge bearbeiten, Flüge anlegen, Flüge bearbeiten, Reporting einsehen, Log-Datei einsehen, Personalaccounts anlegen, Personalaccounts bearbeiten

Die Login-Funktionen werden aktuell im Branch "user_authentication" entwickelt.


## Team

### Vorstellung

Clara Gauer, gauer03@ads.uni-passau.de, gauerla

Dani Lippmann, lippma05@ads.uni-passau.de, danilippmann

Meriem Abbassi, abbass01@ads.uni-passau.de, Meriem-01

Marin Vrdoljak, vrdolj02@ads.uni-passau.de, marinvrdoljak

Claudius Gerstenkorn, gerste04@ads.uni-passau.de, ClaudiusGerstenkorn


### Zuständigkeiten

Clara Gauer: Projektmanagement, Technische Koordination, Backend-Development

Dani Lippmann: Backend-Development

Meriem Abbassi: Datenbank

Marin Vrdoljak: Projektdokumentation, Technische Systemdokumentation, Präsentationen

Claudius Gerstenkorn: Frontend-Development


## Guidelines zur Nutzung dieses Repositorys

### Allgemeine Hinweise und Vorgaben

* Das Repository besteht im initialen Stand aus einem einzelnen Main-Branch. Versuchen Sie bei der Arbeit am Projekt darauf zu achten, dass sich in diesem Branch stets die aktuelle lauffähige und fehlerfreie Version Ihrer Anwendung befindet. Nutzten Sie für die eigentliche Entwicklung ggf. weitere Branches.
* Gehen Sie sorgfältig bei der Erstellung von Issues und *Commit Messages* vor: Die Qualität dieser Artefakte fließt nicht in die Bewertung ein, trotzdem sollten Sie versuchen, Ihr Vorgehen anhand nachvollziehbarer Versionseinträge und klarere Aufgabenbeschreibung gut zu dokumentieren.
* Halten Sie diese und ggf. weitere Readme-Datei(en) stets aktuell.
* Diese sollte auch wichtige Informationen für die Nutzung und die initiale Inbetriebnahme beinhalten (Handbuch).
* Achten Sie insbesondere darauf anzugeben, welche externen Abhängikeiten oder Frameworks ihrem Projekt zugrunde liegen sowie auf die Lesbarkeit ihres finalen Codes.
