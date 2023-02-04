from website.model.models import Flughafen

flughafen = Flughafen.query.get()
for f in flughafen:
    print(f.name)
