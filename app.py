from flask import Flask, render_template
import os
from dotenv import load_dotenv
import tests.sample_data

# Configuration
load_dotenv()  # loads environmental variables from .env
app = Flask(__name__)


# Routes
@app.route('/')
def index():
  return render_template('index.j2')

@app.route('/pokemon')
def pokemon():
  return render_template('pokemon.j2', all_pokemon=tests.sample_data.pokemon)

@app.route('/pokebattles')
def pokebattles():
  return render_template('pokebattles.j2', pokebattles=tests.sample_data.pokemon_battles)

@app.route('/trainers')
def trainers():
  return render_template('trainers.j2', trainers=tests.sample_data.trainers)

@app.route('/battles')
def battles():
  return render_template('battles.j2', battles=tests.sample_data.battles)

@app.route('/species')
def species():
  return render_template('species.j2', all_species=tests.sample_data.species)

@app.route('/addspecies')
def addspecies():
  return render_template('forms/addspecies.j2', types=tests.sample_data.types)

@app.route('/updatespecies')
def updatespecies():
  return render_template('forms/updatespecies.j2')

@app.route('/stadiums')
def stadiums():
  return render_template('stadiums.j2', stadiums=tests.sample_data.stadiums)


# Listener
if __name__ == '__main__':
  port = os.getenv("PORT")  # set port in .env file as PORT=xxxxx

  app.run(port=port, debug=True)