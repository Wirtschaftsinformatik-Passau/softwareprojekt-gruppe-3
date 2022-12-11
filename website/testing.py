from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from .models import Flug, Flughafen, Flugzeug
from . import db

flughafen = Flughafen.query.get()
for f in flughafen:
    print(f.name)
