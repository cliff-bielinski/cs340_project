# Citations:
# Date 6/6/22
# The db configuration code and route functions are adapted from the following:
# OSU CS340 Flask Starter App
# https://github.com/osu-cs340-ecampus/flask-starter-app


import MySQLdb
from flask import Flask, render_template, jsonify, request, redirect
import os
from dotenv import load_dotenv
import tests.sample_data
from flask_mysqldb import MySQL

# Configuration
load_dotenv()  # loads environmental variables from .env
app = Flask(__name__)

# get db configuration variables from .env file
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
  # renders home page with introduction to PokeBattles
  return render_template('index.j2')

@app.route('/pokemon')
def pokemon():
  # renders the pokemon page which displays current Pokemon in Pokemons

  # READ operation for all Pokemon in Pokemons and saved as variable
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

  # READ operation for all Species in Species and saved as variable
  query = "SELECT * FROM Species;"
  cur.execute(query)
  db_species = cur.fetchall()
  
  # READ operation for all Trainers in Trainers and saved as variable
  query = "SELECT * FROM Trainers;"
  cur.execute(query)
  db_trainers = cur.fetchall()

  # search functionality for Pokemons page
  found_pokemon = ""
  search_query = request.args

  # get search parameters if they exist
  if search_query:
    # get search parameters entered by user in form
    search_nickname = search_query["nickname"]
    search_species = search_query["species"]
    search_trainer = search_query["trainer"]
    search_level = search_query["level"]

    # append search parameters to arguments if they exist to create SQL search query
    where_clause =''
    arguments = []  # arguments = (search_nickname, search_species, search_trainer, search_level)
    if search_nickname:
      where_clause += 'nickname = %s and '
      arguments.append(search_nickname)

    where_clause += 'species = %s'
    arguments.append(search_species)
    
    if search_trainer != "None":
      where_clause += ' and Trainers.name = %s'
      arguments.append(search_trainer)
    else:
      where_clause += ' and Trainers.name IS NULL'

    if search_level:
      where_clause += ' and level = %s'
      arguments.append(search_level)

    # READ query that selects Pokemon based on above search parameters
    query = """
      SELECT * FROM `Pokemons` 
      INNER JOIN `Species` ON Species.pokedex_id = Pokemons.pokedex_id
      LEFT JOIN `Trainers` ON Trainers.trainer_id = Pokemons.trainer_id
      WHERE {where_clause};
    """
    query = query.format(where_clause=where_clause)
    cur.execute(query, arguments)
    found_pokemon = cur.fetchall()
    print("-- ", found_pokemon)
  
  cur.close()

  # renders pokemon page with all Pokemon and found Pokemon from search
  return render_template(
    'pokemon.j2',
    all_pokemon=db_pokemons,
    all_species=db_species,
    trainers=db_trainers,
    found_pokemon=found_pokemon
  )


@app.route('/addpokemon', methods=["POST", "GET"])
def addpokemon():
  # this function adds a new pokemon to the database based on user input

  if request.method == "POST":
    # gets user input from HTML form to add new Pokemon
    input_nickname = request.form["nickname"]
    input_species = request.form['species']
    input_trainer = request.form['trainer']
    input_level = request.form['level']
    input_gender = request.form['gender']

    if input_gender == 'None':
      input_gender = None
    
    if not input_nickname:
      input_nickname = None

    # SQL query to add a new Pokemon to the db
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

    cur.close()
    return redirect('/pokemon')

  # get species and trainers for the Add Pokemon form
  query = "SELECT * FROM Species;"
  cur = mysql.connection.cursor()
  cur.execute(query)
  db_species = cur.fetchall()

  query = "SELECT * FROM Trainers;"
  cur.execute(query)
  db_trainers = cur.fetchall()

  cur.close()

  # renders the add Pokemon form with populated list of Trainers and Species to choose as FKs
  return render_template(
    'forms/addpokemon.j2',
    all_species=db_species,
    trainers=db_trainers
  )


@app.route('/updatepokemon/<int:id>', methods=["POST", "GET"])
def updatepokemon(id):

  # display the Update Pokemon form with pre-populated data
  if request.method == "GET":

    # get the target pokemon for update
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

    # get all species and trainer for drop down menus in Update Pokemon form
    query = "SELECT * FROM Species;"
    cur.execute(query)
    db_species = cur.fetchall()

    query = "SELECT * FROM Trainers;"
    cur.execute(query)
    db_trainers = cur.fetchall()

    cur.close()

    # renders the Update Pokemon page with Trainers and Species as options for FKs
    return render_template(
      'forms/updatepokemon.j2',
      pokemon = db_pokemon,
      all_species=db_species,
      trainers=db_trainers
    )

  # update a pokemon
  if request.method == "POST":
    # gets form input from user to update Pokemon
    input_nickname = request.form["nickname"]
    input_species = request.form['species']
    input_trainer = request.form['trainer']
    input_level = request.form['level']
    input_gender = request.form['gender']

    if input_gender == 'None':
      input_gender = None

    if not input_nickname:
      input_nickname = None

    # Update Pokemon SQL query
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

    cur.close()
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
  # SQL query to get all pokebattles from the db and display them
  query = """
    SELECT 
      `pokebattle_id`,
      Battles.date AS `date`, 
      Stadiums.name AS `stadium`,
      Pokemons.nickname AS 'nickname',
      Species.species AS `species`,
      Trainers.name AS `trainer`,
      (Trainers.trainer_id = Battles.winning_trainer) AS `winner`,
      `knocked_out`
    FROM `Pokemons_Battles`
    INNER JOIN `Battles` ON Battles.battle_id = Pokemons_Battles.battle_id
    INNER JOIN `Stadiums` ON Stadiums.stadium_id = Battles.stadium_id
    INNER JOIN `Pokemons` ON Pokemons.pokemon_id = Pokemons_Battles.pokemon_id
    INNER JOIN `Trainers` ON Trainers.trainer_id = Pokemons.trainer_id
    INNER JOIN `Species` ON Species.pokedex_id = Pokemons.pokedex_id;
  """
  cur = mysql.connection.cursor()
  cur.execute(query)
  db_pokebattles = cur.fetchall()
  cur.close()

  # render pokebattle page with table of current pokebattles from db
  return render_template('pokebattles.j2', pokebattles=db_pokebattles)

@app.route('/addpokebattle/<int:id>', methods=["POST", "GET"])
def addpokebattle(id):
  # display the form to add a Pokebattle with prepopulated data
  if request.method == "GET":
    # get the target pokemon to prepopulate form
    query = """
      SELECT `pokemon_id`, `nickname`, Species.species AS `species`, Trainers.name AS trainer, Pokemons.trainer_id AS `trainer_id`
      FROM `Pokemons` 
      LEFT JOIN `Trainers` ON Trainers.trainer_id = Pokemons.trainer_id
      INNER JOIN `Species` ON Species.pokedex_id = Pokemons.pokedex_id
      WHERE `pokemon_id` = %s;
    """
    cur = mysql.connection.cursor()
    cur.execute(query, (id,))
    db_pokemon = cur.fetchone()

    # get the battles available for a particular trainer
    query = """
      SELECT `battle_id`, `date`, Stadiums.name AS `stadium`
      FROM `Battles`
      INNER JOIN `Stadiums` ON Stadiums.stadium_id = Battles.stadium_id
      WHERE `winning_trainer` = %s OR `losing_trainer` = %s;
    """
    
    cur.execute(query, (db_pokemon['trainer_id'], db_pokemon['trainer_id'],))
    db_battles = cur.fetchall()
    cur.close()

    # render add pokebattle page for given pokemon and pass a list of available battles to add as an FK
    return render_template('forms/addpokebattle.j2', pokemon=db_pokemon, battles=db_battles)
  
  # send form data with new pokebattle entry
  if request.method == "POST":
    # get form data for Add Pokebattle from user
    input_battle_id = request.form["battle"]
    input_ko = request.form["knocked-out"]

    # SQL query to add new entry to Pokemons_Battles
    query = """
      INSERT INTO `Pokemons_Battles` (
        `battle_id`,
        `pokemon_id`,
        `knocked_out`
      )
      VALUES (
        (SELECT `battle_id` FROM `Battles` WHERE `battle_id` = %s),
        (SELECT `pokemon_id` FROM `Pokemons` WHERE `pokemon_id` = %s),
        %s
      );
    """
    cur = mysql.connection.cursor()
    cur.execute(query, (input_battle_id, id, input_ko))
    mysql.connection.commit()
    cur.close()
    return redirect('/pokebattles')

@app.route('/updatepokebattle/<int:id>', methods=["POST", "GET"])
def updatepokebattle(id):
  # display the form to update a pokemons_battles entry with prepopulated data
  if request.method == "GET":
    # get the target pokemon to pre-populate the update form
    query = """
      SELECT 
        `pokebattle_id`,
        Battles.date AS `date`, 
        Pokemons_Battles.battle_id AS `battle_id`,
        Stadiums.name AS `stadium`,
        Pokemons.nickname AS 'nickname',
        Species.species AS `species`,
        Trainers.name AS `trainer`,
        Trainers.trainer_id AS `trainer_id`,
        `knocked_out`
      FROM `Pokemons_Battles`
      INNER JOIN `Battles` ON Battles.battle_id = Pokemons_Battles.battle_id
      INNER JOIN `Stadiums` ON Stadiums.stadium_id = Battles.stadium_id
      INNER JOIN `Pokemons` ON Pokemons.pokemon_id = Pokemons_Battles.pokemon_id
      INNER JOIN `Trainers` ON Trainers.trainer_id = Pokemons.trainer_id
      INNER JOIN `Species` ON Species.pokedex_id = Pokemons.pokedex_id
      WHERE `pokebattle_id` = %s;
    """
    cur = mysql.connection.cursor()
    cur.execute(query, (id,))
    db_pokebattle = cur.fetchone()

    # get the battles available for particular trainer
    query = """
      SELECT `battle_id`, `date`, Stadiums.name AS `stadium`
      FROM `Battles`
      INNER JOIN `Stadiums` ON Stadiums.stadium_id = Battles.stadium_id
      WHERE `winning_trainer` = %s OR `losing_trainer` = %s;
    """
    
    cur.execute(query, (db_pokebattle['trainer_id'], db_pokebattle['trainer_id'],))
    db_battles = cur.fetchall()
    cur.close()

    # render the update pokebattles form with given pokebattle data and a list of available battles as FK options
    return render_template('forms/updatepokebattle.j2', pokebattle=db_pokebattle, battles=db_battles)
  
  # send form data with new pokebattle entry
  if request.method == "POST":
    # get form data from user
    input_battle_id = request.form["battle"]
    input_ko = request.form["knocked-out"]

    # SQL query to update entry in Pokemons_Battles with form data
    query = """
      UPDATE `Pokemons_Battles`
      SET
        `battle_id` = (SELECT `battle_id` FROM `Battles` WHERE `battle_id` = %s),
        `knocked_out` = %s
      WHERE `pokebattle_id` = %s; 
    """
    cur = mysql.connection.cursor()
    cur.execute(query, (input_battle_id, input_ko, id))
    mysql.connection.commit()
    cur.close()
    return redirect('/pokebattles')

@app.route('/deletepokebattle/<int:id>')
def deletepokebattle(id):
  # delete selected pokebattle
  query = "DELETE FROM `Pokemons_Battles` WHERE `pokebattle_id` = %s;"
  cur = mysql.connection.cursor()
  cur.execute(query, (id,))
  mysql.connection.commit()
  cur.close()
  return redirect("/pokebattles")

@app.route('/trainers')
def trainers():
  # READ query to get all entries in Trainers table
  query = """
    SELECT `trainer_id`, `name`, `birthdate`, `gender` FROM `Trainers`;
  """
  cur = mysql.connection.cursor()
  cur.execute(query)
  db_trainers = cur.fetchall()
  cur.close()

  # render Trainers page with table of all entries from Trainers table
  return render_template('trainers.j2', trainers=db_trainers)

@app.route('/addtrainer', methods=["POST", "GET"])
def addtrainer():
  # add a trainer to Trainers table
  if request.method == "POST":
    # get form data from user to add new Trainer
    input_name = request.form["trainer-name"]
    input_birthday = request.form["birthday"]
    input_gender = request.form["gender"]

    # SQL ADD query to add entry into Trainers table
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
    cur.close()
    return redirect('/trainers')

  # render Add Trainer page for user to add new trainer
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
    cur.close()
    
    # render the update trainer page with prepopulated data from chosen trainer
    return render_template('forms/updatetrainer.j2', trainer=db_trainer)

  if request.method == "POST":
    # get form data from user to update given trainer
    input_name = request.form["trainer-name"]
    input_birthday = request.form["birthday"]
    input_gender = request.form["gender"]

    # SQL UPDATE operation to update given trainer in Trainers
    query = """
      UPDATE `Trainers`
      SET `name` = %s, `birthdate` = %s, `gender` = %s
      WHERE `trainer_id` = %s;
    """
    cur = mysql.connection.cursor()
    cur.execute(query, (input_name, input_birthday, input_gender, id))
    mysql.connection.commit()
    cur.close()
    return redirect('/trainers')

@app.route("/deletetrainer/<int:id>")
def deletetrainer(id):
    # delete selected trainer from Trainers
    query = "DELETE FROM `Trainers` WHERE `trainer_id` = %s;"
    cur = mysql.connection.cursor()
    cur.execute(query, (id,))
    mysql.connection.commit()
    cur.close()
    return redirect("/trainers")

@app.route('/battles')
def battles():
  # get battles from Battles table and display them

  # SQL READ query to get all battles from Battles
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
  cur.close()

  # render Battles page with all entries from Battles table
  return render_template('battles.j2', battles=db_battles)

@app.route('/addbattle', methods=["POST", "GET"])
def addbattle():
  # add a battle to the database
  if request.method == "POST":
    # get user form data to add a new battle to Battles
    input_date = request.form['date']
    input_location = request.form['location']
    input_winner = request.form['winner']
    input_loser = request.form['loser'] 

    # SQL ADD query to add new battle to Battles
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
    cur.close()
    return redirect('/battles')

  # get trainers and stadiums for population of drop down menus in add battle form (these are FKs)
  query = "SELECT * FROM Trainers;"
  cur = mysql.connection.cursor()
  cur.execute(query)
  db_trainers = cur.fetchall()
  query = "SELECT * FROM Stadiums;"
  
  cur.execute(query)
  db_stadiums = cur.fetchall()
  cur.close()

  # render add battle page with list of trainers and stadiums to populate drop down selection of FKs
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

    # get trainers and stadiums for population of drop down menus for the update battle form
    query = "SELECT * FROM Trainers;"
    cur.execute(query)
    db_trainers = cur.fetchall()
    query = "SELECT * FROM Stadiums;"
    cur.execute(query)
    db_stadiums = cur.fetchall()
    cur.close()

    # render Update Battle page with prepopulated data from selected battle and list of stadiums and trainers for selection by user
    return render_template(
      'forms/updatebattle.j2', 
      battle=db_battle,
      locations=db_stadiums,
      trainers=db_trainers
    )
  
  # update an existing battle
  if request.method == "POST":
    # get form data from user to update battle
    input_date = request.form['date']
    input_location = request.form['location']
    input_winner = request.form['winner']
    input_loser = request.form['loser'] 

    # SQL UPDATE query to update existing battle with user form data
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
    cur.close()
    return redirect('/battles')  

@app.route("/deletebattle/<int:id>")
def deletebattle(id):
    # delete selected battle from Battles table
    query = "DELETE FROM `Battles` WHERE `battle_id` = %s;"
    cur = mysql.connection.cursor()
    cur.execute(query, (id,))
    mysql.connection.commit()
    cur.close()
    return redirect("/battles")

@app.route('/species')
def species():
  # READ query to get all species from Species
  query = """
    SELECT `pokedex_id`, `species`, `type`, `secondary_type` FROM `Species`
    ORDER BY `pokedex_id`;
  """
  cur = mysql.connection.cursor()
  cur.execute(query)
  db_species = cur.fetchall()
  cur.close()

  # render Species page with all existing entries from Species table
  return render_template('species.j2', all_species=db_species)

@app.route('/addspecies', methods=["POST", "GET"])
def addspecies():
  # adding a new species to Species
  if request.method == "POST":
    # get user form data to add new Species
    input_id = request.form['pokedex-id']
    input_species = request.form['species']
    input_type = request.form['type']
    input_sec_type = request.form['secondary-type']

    if input_sec_type == "None":
      input_sec_type = None
    
    # SQL CREATE query to add new species to Species
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
    cur.close()
    return redirect('/species')

  if request.method == "GET":
    # get a list of already used unique pokedex_ids to use when creating a new species entry 
    query = """
      SELECT `pokedex_id`FROM `Species`
      ORDER BY `pokedex_id`;
    """
    cur = mysql.connection.cursor()
    cur.execute(query)
    db_pokedex = cur.fetchall()
    cur.close()

    # create a list of unused pokedex_ids that are available for user when creating a new species entry
    taken_pokedex = []
    for i in db_pokedex:
      taken_pokedex.append(i["pokedex_id"])
    available_pokedex = []
    for i in range(1, 151):
      if i not in taken_pokedex:
        available_pokedex.append(i) 

    # render Add Species page with list of available pokedex_ids for user when adding new species
    return render_template('forms/addspecies.j2', available_pokedex=available_pokedex, types=tests.sample_data.types)

@app.route('/updatespecies/<int:id>', methods=["POST", "GET"])
def updatespecies(id):
  # update an existing species entry

  # get existing attributes of a given species to update
  if request.method == 'GET':
    # get species data to pre-populate update form with existing attributes
    query = """
      SELECT `pokedex_id`, `species`, `type`, `secondary_type`
      FROM `Species` WHERE `pokedex_id` = %s;
    """
    cur = mysql.connection.cursor()
    cur.execute(query, (id,))
    db_species = cur.fetchone()
    cur.close()

    # render the update species page with existing attribute data of species to update
    return render_template(
      'forms/updatespecies.j2', 
      types=tests.sample_data.types,
      species=db_species
    )

  # update existing species with new data
  if request.method == "POST":
    # get form data from user to update species
    input_species = request.form['species']
    input_type = request.form['type']
    input_sec_type = request.form['secondary-type']

    if input_sec_type == "None":
      input_sec_type = None
    
    # UPDATE query to update species with user's form data
    query = """
      UPDATE `Species` 
      SET `species` = %s, `type` = %s, `secondary_type` = %s
      WHERE `pokedex_id` = %s;
    """
    cur = mysql.connection.cursor()
    cur.execute(query, (input_species, input_type, input_sec_type, id))
    mysql.connection.commit()
    cur.close()
    return redirect('/species')

@app.route("/deletespecies/<int:id>")
def deletespecies(id):
    # deletes selected Species by pokedex_id
    query = "DELETE FROM `Species` WHERE `pokedex_id` = %s"
    cur = mysql.connection.cursor()
    cur.execute(query, (id,))
    mysql.connection.commit()
    cur.close()
    return redirect("/species")

@app.route('/stadiums')
def stadiums():
  # display all existing stadiums for user

  # READ query to get all stadiums in Stadiums
  query = """
    SELECT `stadium_id`, `name`, `location` FROM `Stadiums`;
  """
  cur = mysql.connection.cursor()
  cur.execute(query)
  db_stadiums = cur.fetchall()
  cur.close()
  
  # render Stadiums page with all stadiums
  return render_template('stadiums.j2', stadiums=db_stadiums)

@app.route('/addstadium', methods=["POST", "GET"])
def addstadium():
  # adding a new stadium to Stadiums
  if request.method == "POST":
    # get form data from user to add new stadium
    input_name = request.form['stadium-name']
    input_location = request.form['location']

    # CREATE query to add new stadium to Stadiums
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
    cur.close()
    return redirect('/stadiums')

  # render add stadium page
  return render_template('forms/addstadium.j2')

@app.route('/updatestadium/<int:id>', methods=["POST", "GET"])
def updatestadium(id):
  # allows user to update an existing stadium with new data

  if request.method == 'GET':
    # READ query to get current attributes from selected stadium
    query = """
      SELECT `stadium_id`, `name`, `location`
      FROM `Stadiums` WHERE `stadium_id` = %s;
    """
    cur = mysql.connection.cursor()
    cur.execute(query, (id,))
    db_stadiums = cur.fetchone()
    cur.close()

    # render Update stadiums page with pre-populated attributes of selected stadium for update
    return render_template('forms/updatestadium.j2', stadiums=db_stadiums)
  
  # update stadium with new form data
  if request.method == "POST":
    # get form data from user to update stadium
    input_name = request.form['stadium-name']
    input_location = request.form['location']

    # UPDATE query to update a given stadium in Stadiums
    query = """
      UPDATE `Stadiums` 
      SET `name` = %s, `location` = %s
      WHERE `stadium_id` = %s;
    """
    cur = mysql.connection.cursor()
    cur.execute(query, (input_name, input_location, id))
    mysql.connection.commit()
    cur.close()
    return redirect('/stadiums')

@app.route("/deletestadium/<int:id>")
def deletestadium(id):
    # deletes selected stadium by stadium_id
    query = "DELETE FROM `Stadiums` WHERE `stadium_id` = %s;"
    cur = mysql.connection.cursor()
    cur.execute(query, (id,))
    mysql.connection.commit()
    cur.close()
    return redirect("/stadiums")

# Error Handling for MySQL DB errors
@app.errorhandler(MySQLdb.Error)
def internal_error(error):
  # displays error message to user when MySQL error encountered
  return render_template('error.j2', error=error), 500

# Listener
if __name__ == '__main__':
  port = os.getenv("PORT")  # set port in .env file as PORT=xxxxx

  app.run(port=port, debug=True)