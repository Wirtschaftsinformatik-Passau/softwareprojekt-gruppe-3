from website.models import Flug, Flughafen, Flugzeug


flughafen = Flughafen.query.get()
for f in flughafen:
    print(f.name)
