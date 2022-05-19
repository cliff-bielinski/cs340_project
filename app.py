from flask import Flask, render_template, json, request, redirect
import os
from dotenv import load_dotenv
import tests.sample_data
from flask_mysqldb import MySQL

# Configuration
load_dotenv()  # loads environmental variables from .env
app = Flask(__name__)

app.config["MYSQL_HOST"] = os.getenv("host")
app.config["MYSQL_USER"] = os.getenv("user")
app.config["MYSQL_PASSWORD"] = os.getenv("passwd")
app.config["MYSQL_DB"] = os.getenv("db")
app.config["MYSQL_CURSORCLASS"] = "DictCursor"
mysql = MySQL(app)

# Routes
@app.route('/')
def index():
  return render_template('index.j2')

@app.route('/pokemon')
def pokemon():
  query = """
    SELECT `pokemon_id`, `nickname`, Pokemons.gender, `level`, Species.species, Trainers.name AS trainer
    FROM `Pokemons` 
    INNER JOIN `Species` ON Species.pokedex_id = Pokemons.pokedex_id
    LEFT JOIN `Trainers` ON Trainers.trainer_id = Pokemons.trainer_id
    ORDER BY `pokemon_id`;
  """
  cur = mysql.connection.cursor()
  cur.execute(query)
  db_pokemons = cur.fetchall()

  # query = "SELECT * FROM Species;"
  # cur = mysql.connection.cursor()
  # cur.execute(query)
  # db_species = cur.fetchall()
  
  # query = "SELECT * FROM Trainers;"
  # cur = mysql.connection.cursor()
  # cur.execute(query)
  # db_trainers = cur.fetchall()

  # data_pokemons = []
  # for pokemon in db_pokemons:
  #   cur_pokemon = pokemon
  #   cur_species = None
  #   for species in db_species:
  #     if species['pokedex_id'] == cur_pokemon['pokedex_id']:
  #         cur_species = species['species']

  #   cur_trainer = None
  #   for trainer in db_trainers:
  #     if trainer['trainer_id'] == cur_pokemon['trainer_id']:
  #         cur_trainer = trainer['name']
  #   cur_pokemon['species'] = cur_species
  #   cur_pokemon['trainer'] = cur_trainer
  #   data_pokemons.append(cur_pokemon)

  return render_template(
    'pokemon.j2',
    all_pokemon=db_pokemons
    )


@app.route('/addpokemon', methods=["POST", "GET"])
def addpokemon():

  # to add a pokemon
  if request.method == "POST":
    input_nickname = request.form["nickname"]
    input_species = request.form['species']
    input_trainer = request.form['trainer']
    input_level = request.form['level']
    input_gender = request.form['gender']

    if input_gender == 'None':
      input_gender = None

    query = "SELECT pokedex_id FROM Species where species=%s"
    cur = mysql.connection.cursor()
    cur.execute(query, (input_species,))
    db_species_tuple = cur.fetchall()  # got back a tuple ({'pokedex_id': 1},)
    if db_species_tuple:
        input_species = db_species_tuple[0]['pokedex_id']
    else:
      input_species = None

    query = "SELECT trainer_id FROM Trainers where name=%s"
    cur = mysql.connection.cursor()
    cur.execute(query, (input_trainer,))
    db_trainers_tuple = cur.fetchall()  # got back a tuple of 1 dictionary element ({'trainer_id': 1},)
    if db_trainers_tuple:
      input_trainer = db_trainers_tuple[0]['trainer_id'] 
    else:
      input_trainer = None

    query = "INSERT INTO Pokemons (nickname, gender, level, pokedex_id, trainer_id) VALUES (%s, %s, %s, %s, %s)"
    cur = mysql.connection.cursor()
    cur.execute(query, (input_nickname, input_gender, input_level, input_species, input_trainer))
    mysql.connection.commit()

    return redirect('/pokemon')

  # to display the form
  return render_template(
    'forms/addpokemon.j2',
    all_species=tests.sample_data.species,
    trainers=tests.sample_data.trainers
  )


@app.route('/updatepokemon/<int:id>', methods=["POST", "GET"])
def updatepokemon(id):

  # display the form with pre-populated data
  if request.method == "GET":

    # get the target pokemon
    query = """
      SELECT `pokemon_id`, `nickname`, Pokemons.gender, `level`, Species.species, Trainers.name AS trainer
      FROM `Pokemons` 
      INNER JOIN `Species` ON Species.pokedex_id = Pokemons.pokedex_id
      LEFT JOIN `Trainers` ON Trainers.trainer_id = Pokemons.trainer_id
      WHERE `pokemon_id` = %s
    """
    cur = mysql.connection.cursor()
    cur.execute(query, (id,))
    db_pokemon = cur.fetchone()

    # # get species name and trainer name
    # query = "SELECT species FROM Species where pokedex_id=%s;"
    # cur = mysql.connection.cursor()
    # cur.execute(query, (db_pokemon['pokedex_id'], ))
    # db_species = cur.fetchone()  # got back dictionary {'species': 'Bulbasaur'}
    # query = "SELECT name FROM Trainers where trainer_id=%s;"
    # cur = mysql.connection.cursor()
    # cur.execute(query, (db_pokemon['trainer_id'], ))
    # db_trainer = cur.fetchone()

    # db_pokemon['species'] = db_species['species']
    # if db_trainer:
    #   db_pokemon['trainer'] = db_trainer['name']
    # else:
    #   db_pokemon['trainer'] = None

    # get all species and trainer
    query = "SELECT * FROM Species;"
    cur = mysql.connection.cursor()
    cur.execute(query)
    db_species = cur.fetchall()
    query = "SELECT * FROM Trainers;"
    cur = mysql.connection.cursor()
    cur.execute(query)
    db_trainers = cur.fetchall()

    return render_template(
      'forms/updatepokemon.j2',
      pokemon = db_pokemon,
      all_species=db_species,
      trainers=db_trainers
    )

  # update a pokemon
  if request.method == "POST":
    input_nickname = request.form["nickname"]
    input_species = request.form['species']
    input_trainer = request.form['trainer']
    input_level = request.form['level']
    input_gender = request.form['gender']

    if input_gender == 'None':
      input_gender = None

    # # get species id and trainer id
    # species_id = None
    # trainer_id = None
    # query = "SELECT pokedex_id FROM Species where species=%s"
    # cur = mysql.connection.cursor()
    # cur.execute(query, (input_species,))
    # db_species = cur.fetchone()  # got back a dictionary {'pokedex_id': 1}
    # if db_species:
    #     species_id = db_species['pokedex_id']

    # if input_trainer != 'None':
    #   query = "SELECT trainer_id FROM Trainers where name=%s"
    #   cur = mysql.connection.cursor()
    #   cur.execute(query, (input_trainer,))
    #   db_trainers = cur.fetchone()  # got back a dictionary {'trainer_id': 1}
    #   trainer_id = db_trainers['trainer_id'] 
    # else:
    #   trainer_id = None


    query = """
      UPDATE `Pokemons`
      SET 
        `nickname` = %s,
        `gender` = %s,
        `level` = %s,
        `pokedex_id` = (SELECT `pokedex_id` FROM `Species` WHERE `species` = %s),
        `trainer_id` = (SELECT `trainer_id` FROM `Trainers` WHERE `name` = %s)
      WHERE `pokemon_id` = %s;
    """
    # query = "UPDATE Pokemons SET nickname = %s, gender = %s, level = %s, pokedex_id = %s, trainer_id = %s WHERE pokemon_id = %s"
    cur = mysql.connection.cursor()
    cur.execute(query, (input_nickname, input_gender, input_level, input_species, input_trainer, id))
    mysql.connection.commit()

    return redirect('/pokemon')  


@app.route("/deletepokemon/<int:id>")
def deletepokemon(id):
    query = "DELETE FROM Pokemons WHERE pokemon_id = '%s';"
    cur = mysql.connection.cursor()
    cur.execute(query, (id,))
    mysql.connection.commit()

    return redirect("/pokemon")



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