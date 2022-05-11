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
  return render_template(
    'pokemon.j2',
    all_pokemon=tests.sample_data.pokemon,
    all_species=tests.sample_data.species,
    trainers=tests.sample_data.trainers
    )

@app.route('/addpokemon')
def addpokemon():
  return render_template(
    'forms/addpokemon.j2',
    all_species=tests.sample_data.species,
    trainers=tests.sample_data.trainers
  )

@app.route('/updatepokemon')
def updatepokemon():
  return render_template(
    'forms/updatepokemon.j2',
    all_species=tests.sample_data.species,
    trainers=tests.sample_data.trainers
  )

@app.route('/pokebattles')
def pokebattles():
  return render_template('pokebattles.j2', pokebattles=tests.sample_data.pokemon_battles)

@app.route('/addpokebattle')
def addpokebattle():
  return render_template('forms/addpokebattle.j2')

@app.route('/updatepokebattle')
def updatepokebattle():
  return render_template('forms/updatepokebattle.j2')

@app.route('/trainers')
def trainers():
  return render_template('trainers.j2', trainers=tests.sample_data.trainers)

@app.route('/addtrainer')
def addtrainer():
  return render_template('forms/addtrainer.j2')

@app.route('/updatetrainer')
def updatetrainer():
  return render_template('forms/updatetrainer.j2')

@app.route('/battles')
def battles():
  return render_template('battles.j2', battles=tests.sample_data.battles)

@app.route('/addbattle')
def addbattle():
  return render_template(
    'forms/addbattle.j2', 
    locations=tests.sample_data.stadiums,
    trainers=tests.sample_data.trainers
  )

@app.route('/updatebattle')
def updatebattle():
  return render_template(
    'forms/updatebattle.j2', 
    locations=tests.sample_data.stadiums,
    trainers=tests.sample_data.trainers
  )

@app.route('/species')
def species():
  return render_template('species.j2', all_species=tests.sample_data.species)

@app.route('/addspecies')
def addspecies():
  return render_template('forms/addspecies.j2', types=tests.sample_data.types)

@app.route('/updatespecies')
def updatespecies():
  return render_template('forms/updatespecies.j2', types=tests.sample_data.types)

@app.route('/stadiums')
def stadiums():
  return render_template('stadiums.j2', stadiums=tests.sample_data.stadiums)

@app.route('/addstadium')
def addstadium():
  return render_template('forms/addstadium.j2')

@app.route('/updatestadium')
def updatestadium():
  return render_template('forms/updatestadium.j2')

# Listener
if __name__ == '__main__':
  port = os.getenv("PORT")  # set port in .env file as PORT=xxxxx

  app.run(port=port, debug=True)