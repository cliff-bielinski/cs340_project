from flask import Flask, render_template, json, request, redirect
import os
from dotenv import load_dotenv
import tests.sample_data
import database.db_connector as db
from flask_mysqldb import MySQL

# Configuration
load_dotenv()  # loads environmental variables from .env
app = Flask(__name__)
# db_connection = db.connect_to_database() # YUJUN this line breaks

# YUJUN
app.config["MYSQL_HOST"] = "classmysql.engr.oregonstate.edu"
app.config["MYSQL_USER"] = "cs340_liuyuju"
app.config["MYSQL_PASSWORD"] = "3754"
app.config["MYSQL_DB"] = "cs340_liuyuju"
app.config["MYSQL_CURSORCLASS"] = "DictCursor"
mysql = MySQL(app)

# Routes
@app.route('/')
def index():
  return render_template('index.j2')

@app.route('/test')
def test():
  query = "SELECT * FROM Stadiums;"
  cursor = db.execute_query(db_connection=db_connection, query=query)
  results = json.dumps(cursor.fetchall())
  return results

@app.route('/pokemon')
def pokemon():
  query = "SELECT * FROM Pokemons;"
  cur = mysql.connection.cursor()
  cur.execute(query)
  db_pokemons = cur.fetchall()

  query = "SELECT * FROM Species;"
  cur = mysql.connection.cursor()
  cur.execute(query)
  db_species = cur.fetchall()
  
  query = "SELECT * FROM Trainers;"
  cur = mysql.connection.cursor()
  cur.execute(query)
  db_trainers = cur.fetchall()

  data_pokemons = []
  for pokemon in db_pokemons:
    cur_pokemon = pokemon
    cur_species = None
    for species in db_species:
      if species['pokedex_id'] == cur_pokemon['pokedex_id']:
          cur_species = species['species']

    cur_trainer = None
    for trainer in db_trainers:
      if trainer['trainer_id'] == cur_pokemon['trainer_id']:
          cur_trainer = trainer['name']
    cur_pokemon['species'] = cur_species
    cur_pokemon['trainer'] = cur_trainer
    data_pokemons.append(cur_pokemon)
  
  # print(data_pokemons)
  # print(db_species)
  # print(db_trainers)

  return render_template(
    'pokemon.j2',
    all_pokemon=data_pokemons,
    all_species=db_species,
    trainers=db_trainers
    )

@app.route('/addpokemon', methods=["POST", "GET"])
def addpokemon():
  if request.method == "POST":
    input_nickname = request.form["nickname"]
    input_species = request.form['species']
    input_trainer = request.form['trainer']
    input_level = request.form['level']
    input_gender = request.form['gender']

    # print(input_nickname, input_species, input_trainer, input_level, input_gender)

    if input_gender == 'None':
      input_gender = None

    query = "SELECT pokedex_id FROM Species where species=%s"
    cur = mysql.connection.cursor()
    cur.execute(query, (input_species,))
    db_species_tuple = cur.fetchall()  # got back a tuple ({'pokedex_id': 1},)
    if db_species_tuple:
        # print(db_species_tuple, type(db_species_tuple), db_species_tuple[0]['pokedex_id'])
        input_species = db_species_tuple[0]['pokedex_id']
    else:
      input_species = None

    query = "SELECT trainer_id FROM Trainers where name=%s"
    cur = mysql.connection.cursor()
    cur.execute(query, (input_trainer,))
    db_trainers_tuple = cur.fetchall()  # got back a tuple of 1 dictionary element ({'trainer_id': 1},)
    if db_trainers_tuple:
      # print(db_trainers_tuple, type(db_trainers_tuple), db_trainers_tuple[0]['trainer_id'])
      input_trainer = db_trainers_tuple[0]['trainer_id'] 
    else:
      input_trainer = None



    query = "INSERT INTO Pokemons (nickname, poke_gender, level, pokedex_id, trainer_id) VALUES (%s, %s, %s, %s, %s)"
    cur = mysql.connection.cursor()
    cur.execute(query, (input_nickname, input_gender, input_level, input_species, input_trainer))
    mysql.connection.commit()

    return redirect('/pokemon')

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