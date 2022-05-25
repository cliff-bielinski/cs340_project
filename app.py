import MySQLdb
from flask import Flask, render_template, jsonify, request, redirect
import os
from dotenv import load_dotenv
import tests.sample_data
from flask_mysqldb import MySQL

# Configuration
load_dotenv()  # loads environmental variables from .env
app = Flask(__name__)

app.secret_key = os.getenv("secret_key")
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

  query = "SELECT * FROM Species;"
  cur = mysql.connection.cursor()
  cur.execute(query)
  db_species = cur.fetchall()
  
  query = "SELECT * FROM Trainers;"
  cur = mysql.connection.cursor()
  cur.execute(query)
  db_trainers = cur.fetchall()

  return render_template(
    'pokemon.j2',
    all_pokemon=db_pokemons,
    all_species=db_species,
    trainers=db_trainers
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
    
    if not input_nickname:
      input_nickname = None

    query = """
      INSERT INTO `Pokemons` (
        `nickname`,
        `gender`,
        `level`,
        `pokedex_id`,
        `trainer_id`
      )
      VALUES (
        %s,
        %s,
        %s,
        (SELECT `pokedex_id` FROM `Species` WHERE `species` = %s),
        (SELECT `trainer_id` FROM `Trainers` WHERE `name` = %s)
      );
    """
    cur = mysql.connection.cursor()
    cur.execute(query, (input_nickname, input_gender, input_level, input_species, input_trainer))
    mysql.connection.commit()

    return redirect('/pokemon')

  # get species and trainers for form
  query = "SELECT * FROM Species;"
  cur = mysql.connection.cursor()
  cur.execute(query)
  db_species = cur.fetchall()
  query = "SELECT * FROM Trainers;"
  cur = mysql.connection.cursor()
  cur.execute(query)
  db_trainers = cur.fetchall()

  # to display the form
  return render_template(
    'forms/addpokemon.j2',
    all_species=db_species,
    trainers=db_trainers
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

    if not input_nickname:
      input_nickname = None

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

    cur = mysql.connection.cursor()
    cur.execute(query, (input_nickname, input_gender, input_level, input_species, input_trainer, id))
    mysql.connection.commit()

    return redirect('/pokemon')  


@app.route("/deletepokemon/<int:id>")
def deletepokemon(id):
    # delete selected pokemon
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
  # get all trainers from the database
  query = """
    SELECT `trainer_id`, `name`, `birthdate`, `gender` FROM `Trainers`;
  """
  cur = mysql.connection.cursor()
  cur.execute(query)
  db_trainers = cur.fetchall()
  return render_template('trainers.j2', trainers=db_trainers)

@app.route('/addtrainer', methods=["POST", "GET"])
def addtrainer():
  # add a trainer
  if request.method == "POST":
    input_name = request.form["trainer-name"]
    input_birthday = request.form["birthday"]
    input_gender = request.form["gender"]

    query = """
      INSERT INTO `Trainers` (
        `name`,
        `birthdate`,
        `gender`
      )
      VALUES (%s, %s, %s);
    """
    cur = mysql.connection.cursor()
    cur.execute(query, (input_name, input_birthday, input_gender))
    mysql.connection.commit()

    return redirect('/trainers')

  return render_template('forms/addtrainer.j2')

@app.route('/updatetrainer/<int:id>', methods=["POST", "GET"])
def updatetrainer(id):
  if request.method == "GET":
    # get the target trainer for update
    query = """
      SELECT `trainer_id`, `name`, `birthdate`, `gender`
      FROM `Trainers` WHERE `trainer_id` = %s;
    """
    cur = mysql.connection.cursor()
    cur.execute(query, (id,))
    db_trainer = cur.fetchone()
    
    return render_template('forms/updatetrainer.j2', trainer=db_trainer)

  if request.method == "POST":
    input_name = request.form["trainer-name"]
    input_birthday = request.form["birthday"]
    input_gender = request.form["gender"]

    query = """
      UPDATE `Trainers`
      SET `name` = %s, `birthdate` = %s, `gender` = %s
      WHERE `trainer_id` = %s;
    """
    cur = mysql.connection.cursor()
    cur.execute(query, (input_name, input_birthday, input_gender, id))
    mysql.connection.commit()

    return redirect('/trainers')

@app.route("/deletetrainer/<int:id>")
def deletetrainer(id):
    # delete selected trainer
    query = "DELETE FROM `Trainers` WHERE `trainer_id` = %s;"
    cur = mysql.connection.cursor()
    cur.execute(query, (id,))
    mysql.connection.commit()
    return redirect("/trainers")

@app.route('/battles')
def battles():
  # get battles from database and display them
  query = """
    SELECT `battle_id`, `date`, Stadiums.name AS `location`, winner.name AS `winner`, loser.name AS `loser`
    FROM `Battles` 
    INNER JOIN `Stadiums` ON Stadiums.stadium_id = Battles.stadium_id
    INNER JOIN `Trainers` winner ON winner.trainer_id = Battles.winning_trainer
    INNER JOIN `Trainers` loser ON loser.trainer_id = Battles.losing_trainer
    ORDER BY `battle_id`;
  """
  cur = mysql.connection.cursor()
  cur.execute(query)
  db_battles = cur.fetchall()

  return render_template('battles.j2', battles=db_battles)

@app.route('/addbattle', methods=["POST", "GET"])
def addbattle():
  # add a battle to the database
  if request.method == "POST":
    input_date = request.form['date']
    input_location = request.form['location']
    input_winner = request.form['winner']
    input_loser = request.form['loser'] 

    query = """
      INSERT INTO `Battles` (
        `date`,
        `stadium_id`,
        `winning_trainer`,
        `losing_trainer`
      )
      VALUES (
        %s,
        (SELECT `stadium_id` FROM `Stadiums` WHERE `name` = %s),
        (SELECT `trainer_id` FROM `Trainers` WHERE `name` = %s),
        (SELECT `trainer_id` FROM `Trainers` WHERE `name` = %s)
      );
    """
    cur = mysql.connection.cursor()
    cur.execute(query, (input_date, input_location, input_winner, input_loser))
    mysql.connection.commit()
    return redirect('/battles')

  # get trainers and stadiums for population of add battle form
  query = "SELECT * FROM Trainers;"
  cur = mysql.connection.cursor()
  cur.execute(query)
  db_trainers = cur.fetchall()
  query = "SELECT * FROM Stadiums;"
  cur = mysql.connection.cursor()
  cur.execute(query)
  db_stadiums = cur.fetchall()

  return render_template(
    'forms/addbattle.j2', 
    locations=db_stadiums,
    trainers=db_trainers
  )

@app.route('/updatebattle/<int:id>', methods=["POST", "GET"])
def updatebattle(id):
  if request.method == "GET":
    # get the target battle to update
    query = """
      SELECT `battle_id`, `date`, Stadiums.name AS `location`, winner.name AS `winner`, loser.name AS `loser`
      FROM `Battles` 
      INNER JOIN `Stadiums` ON Stadiums.stadium_id = Battles.stadium_id
      INNER JOIN `Trainers` winner ON winner.trainer_id = Battles.winning_trainer
      INNER JOIN `Trainers` loser ON loser.trainer_id = Battles.losing_trainer
      WHERE `battle_id` = %s;
    """
    cur = mysql.connection.cursor()
    cur.execute(query, (id,))
    db_battle = cur.fetchone()

    # get trainers and stadiums for population of add battle form
    query = "SELECT * FROM Trainers;"
    cur = mysql.connection.cursor()
    cur.execute(query)
    db_trainers = cur.fetchall()
    query = "SELECT * FROM Stadiums;"
    cur = mysql.connection.cursor()
    cur.execute(query)
    db_stadiums = cur.fetchall()

    return render_template(
      'forms/updatebattle.j2', 
      battle=db_battle,
      locations=db_stadiums,
      trainers=db_trainers
    )
  
  if request.method == "POST":
    # update a battle
    input_date = request.form['date']
    input_location = request.form['location']
    input_winner = request.form['winner']
    input_loser = request.form['loser'] 

    query = """
      UPDATE `Battles`
      SET
        `date` = %s,
        `stadium_id` = (SELECT `stadium_id` FROM `Stadiums` WHERE `name` = %s),
        `winning_trainer` = (SELECT `trainer_id` FROM `Trainers` WHERE `name` = %s),
        `losing_trainer` = (SELECT `trainer_id` FROM `Trainers` WHERE `name` = %s)
      WHERE `battle_id` = %s; 
    """

    cur = mysql.connection.cursor()
    cur.execute(query, (input_date, input_location, input_winner, input_loser, id))
    mysql.connection.commit()

    return redirect('/battles')  

@app.route("/deletebattle/<int:id>")
def deletebattle(id):
    # delete selected battle
    query = "DELETE FROM `Battles` WHERE `battle_id` = %s;"
    cur = mysql.connection.cursor()
    cur.execute(query, (id,))
    mysql.connection.commit()
    return redirect("/battles")

@app.route('/species')
def species():
  # get all species from Species
  query = """
    SELECT `pokedex_id`, `species`, `type`, `secondary_type` FROM `Species`
    ORDER BY `pokedex_id`;
  """
  cur = mysql.connection.cursor()
  cur.execute(query)
  db_species = cur.fetchall()

  return render_template('species.j2', all_species=db_species)

@app.route('/addspecies', methods=["POST", "GET"])
def addspecies():
  # adding a new species
  if request.method == "POST":
    input_id = request.form['pokedex-id']
    input_species = request.form['species']
    input_type = request.form['type']
    input_sec_type = request.form['secondary-type']

    if input_sec_type == "None":
      input_sec_type = None
    
    query = """
      INSERT INTO `Species` (
        `pokedex_id`,
        `species`,
        `type`,
        `secondary_type`
      )
      VALUES (%s, %s, %s, %s);
    """
    cur = mysql.connection.cursor()
    cur.execute(query, (input_id, input_species, input_type, input_sec_type))
    mysql.connection.commit()

    return redirect('/species')

  if request.method == "GET":
    query = """
      SELECT `pokedex_id`FROM `Species`
      ORDER BY `pokedex_id`;
    """
    cur = mysql.connection.cursor()
    cur.execute(query)
    db_pokedex = cur.fetchall()
    taken_pokedex = []
    for i in db_pokedex:
      taken_pokedex.append(i["pokedex_id"])
    available_pokedex = []
    for i in range(1, 151):
      if i not in taken_pokedex:
        available_pokedex.append(i) 
    return render_template('forms/addspecies.j2', available_pokedex=available_pokedex, types=tests.sample_data.types)

@app.route('/updatespecies/<int:id>', methods=["POST", "GET"])
def updatespecies(id):
  # display current attributes of species to update
  if request.method == 'GET':
    # get current attributes of species to update
    query = """
      SELECT `pokedex_id`, `species`, `type`, `secondary_type`
      FROM `Species` WHERE `pokedex_id` = %s;
    """
    cur = mysql.connection.cursor()
    cur.execute(query, (id,))
    db_species = cur.fetchone()

    return render_template(
      'forms/updatespecies.j2', 
      types=tests.sample_data.types,
      species=db_species
    )

  if request.method == "POST":
    input_species = request.form['species']
    input_type = request.form['type']
    input_sec_type = request.form['secondary-type']

    if input_sec_type == "None":
      input_sec_type = None
    
    query = """
      UPDATE `Species` 
      SET `species` = %s, `type` = %s, `secondary_type` = %s
      WHERE `pokedex_id` = %s;
    """
    cur = mysql.connection.cursor()
    cur.execute(query, (input_species, input_type, input_sec_type, id))
    mysql.connection.commit()

    return redirect('/species')

@app.route("/deletespecies/<int:id>")
def deletespecies(id):
    # deletes selected Species by pokedex_id
    query = "DELETE FROM `Species` WHERE `pokedex_id` = %s"
    cur = mysql.connection.cursor()
    cur.execute(query, (id,))
    mysql.connection.commit()

    return redirect("/species")

@app.route('/stadiums')
def stadiums():
  # get all stadiums
  query = """
    SELECT `stadium_id`, `name`, `location` FROM `Stadiums`;
  """
  cur = mysql.connection.cursor()
  cur.execute(query)
  db_stadiums = cur.fetchall()

  return render_template('stadiums.j2', stadiums=db_stadiums)

@app.route('/addstadium', methods=["POST", "GET"])
def addstadium():
  # adding a new stadium
  if request.method == "POST":
    input_name = request.form['stadium-name']
    input_location = request.form['location']

    query = """
      INSERT INTO `Stadiums` (
        `name`,
        `location`
      )
      VALUES (%s, %s)
    """
    cur = mysql.connection.cursor()
    cur.execute(query, (input_name, input_location))
    mysql.connection.commit()

    return redirect('/stadiums')

  return render_template('forms/addstadium.j2')

@app.route('/updatestadium/<int:id>', methods=["POST", "GET"])
def updatestadium(id):
  if request.method == 'GET':
    # get current attributes of stadium to update
    query = """
      SELECT `stadium_id`, `name`, `location`
      FROM `Stadiums` WHERE `stadium_id` = %s;
    """
    cur = mysql.connection.cursor()
    cur.execute(query, (id,))
    db_stadiums = cur.fetchone()
    return render_template('forms/updatestadium.j2', stadiums=db_stadiums)
  
  if request.method == "POST":
    # update stadium with new form data
    input_name = request.form['stadium-name']
    input_location = request.form['location']

    query = """
      UPDATE `Stadiums` 
      SET `name` = %s, `location` = %s
      WHERE `stadium_id` = %s;
    """
    cur = mysql.connection.cursor()
    cur.execute(query, (input_name, input_location, id))
    mysql.connection.commit()

    return redirect('/stadiums')

@app.route("/deletestadium/<int:id>")
def deletestadium(id):
    # deletes selected stadium by stadium_id
    query = "DELETE FROM `Stadiums` WHERE `stadium_id` = %s;"
    cur = mysql.connection.cursor()
    cur.execute(query, (id,))
    mysql.connection.commit()

    return redirect("/stadiums")

# Error Handling for MySQL DB errors
@app.errorhandler(MySQLdb.Error)
def internal_error(error):
  return render_template('error.j2', error=error), 500

# Listener
if __name__ == '__main__':
  port = os.getenv("PORT")  # set port in .env file as PORT=xxxxx

  app.run(port=port, debug=True)