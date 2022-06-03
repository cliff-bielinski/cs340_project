-- -----------------------------------------
-- Project Name: PokeBattle
-- Step 3 Draft
-- Group: The 39ers
-- Members: Clifford Bielinski, Yujun Liu
-- -----------------------------------------


-- queries use the notation :variable to denote variables
-- that will have data from the backend programming language

-- -----------------------------------------
-- Species queries 
-- -----------------------------------------
-- get all Species IDs, Species, Type and Secondary Type to populate Current Pokemon Species
SELECT `pokedex_id`, `species`, `type`, `secondary_type` FROM `Species`;

-- get a single Species's data for the Update Species Form
SELECT `pokedex_id`, `species`, `type`, `secondary_type`
FROM `Species` WHERE `pokedex_id` = :pokedex_id_from_browser;

-- update a single Species's data for the Update Species Form
UPDATE `Species` 
SET `species` = :species_input, `type` = :type_input, `secondary_type` = :secondary_type_input
WHERE `pokedex_id` = :pokedex_id_from_browser;

-- insert a new Species for the Add Species Form
INSERT INTO `Species` (
  `pokedex_id`,
  `species`,
  `type`,
  `secondary_type`
)
VALUES (:pokedex_id_input, :species_input, :type_input, :secondary_type_input)

-- delete a Species in Current Species
DELETE FROM `Species` WHERE `pokedex_id` = :pokedex_id_from_browser;

-- -----------------------------------------
-- Stadiums queries 
-- -----------------------------------------
-- get all stadium_id, name, location to populate Current Stadiums
SELECT `stadium_id`, `name`, `location` FROM `Stadiums`;

-- get a single Stadium's data for the Update Stadium Form
SELECT `stadium_id`, `name`, `location`
FROM `Stadiums` WHERE `stadium_id` = :stadium_id_from_browser;

-- update a single Stadium's data for the Update Stadium Form
UPDATE `Stadiums` 
SET `name` = :name_input, `location` = :location_input
WHERE `stadium_id` = :stadium_id_from_browser;

-- insert a new Stadium for the Add Stadium Form
INSERT INTO `Stadiums` (
  `name`,
  `location`
)
VALUES (:name_input, :location_input)

-- delete a Stadium in Current Stadiums
DELETE FROM `Stadiums` WHERE `stadium_id` = :stadium_id_from_browser;

-- -----------------------------------------
-- Trainers queries 
-- -----------------------------------------
-- get all trainer_id, name, birthdate, gender to populate Current Trainers
SELECT `trainer_id`, `name`, `birthdate`, `gender` FROM `Trainers`;

-- get a single Trainer's data for the Update Trainer Form
SELECT `trainer_id`, `name`, `birthdate`, `gender`
FROM `Trainers` WHERE `trainer_id` = :trainer_id_from_browser;

-- update a single Trainer's data for the Update Trainer Form
UPDATE `Trainers`
SET `name` = :name_input, `birthdate` = :birthdate_input, `gender` = :gender_input
WHERE `trainer_id` = :trainer_id_from_browser;

-- insert a new Trainer for the Add Trainer Form
INSERT INTO `Trainers` (
  `name`,
  `birthdate`,
  `gender`
)
VALUES (:name_input, :birthdate_input, :gender_input);

-- delete a Trainer in Current Trainers
DELETE FROM `Trainers` WHERE `trainer_id` = :trainer_id_from_browser;

-- -----------------------------------------
-- Pokemons queries 
-- -----------------------------------------
-- get all pokemon_id, nickname, gender, level, species, trainer to populate Current Pokemon
SELECT `pokemon_id`, `nickname`, Pokemons.gender, `level`, Species.species, Trainers.name AS trainer
FROM `Pokemons` 
INNER JOIN `Species` ON Species.pokedex_id = Pokemons.pokedex_id
LEFT JOIN `Trainers` ON Trainers.trainer_id = Pokemons.trainer_id
ORDER BY `pokemon_id`;

-- get a single Pokemon's data for the Update Pokemon Form
SELECT `pokemon_id`, `nickname`, Pokemons.gender, `level`, Species.species, Trainers.name AS trainer
FROM `Pokemons` 
INNER JOIN `Species` ON Species.pokedex_id = Pokemons.pokedex_id
LEFT JOIN `Trainers` ON Trainers.trainer_id = Pokemons.trainer_id
WHERE `pokemon_id` = :pokemon_id_from_browser;

-- update a single Pokemon's data for the Update Pokemon Form
UPDATE `Pokemons`
SET 
  `nickname` = :nickname_input,
  `gender` = :gender_input,
  `level` = :level_input,
  `pokedex_id` = (SELECT `pokedex_id` FROM `Species` WHERE `species` = :species_input),
  `trainer_id` = (SELECT `trainer_id` FROM `Trainers` WHERE `name` = :name_input)
WHERE `pokemon_id` = :pokemon_id_from_browser;

-- insert a new Pokemon for the Add Pokemon Form
INSERT INTO `Pokemons` (
  `nickname`,
  `gender`,
  `level`,
  `pokedex_id`,
  `trainer_id`
)
VALUES (
  :nickname_input,
  :gender_input,
  :level_input,
  (SELECT `pokedex_id` FROM `Species` WHERE `species` = :species_input),
  (SELECT `trainer_id` FROM `Trainers` WHERE `name` = :name_input)
);

-- delete a Pokemon in Current Pokemon
DELETE FROM `Pokemons` WHERE `pokemon_id` = :pokemon_id_from_browser;

-- -----------------------------------------
-- Battles queries 
-- -----------------------------------------
-- get all battle_id, date, location, winner, loser to populate Current Battles
SELECT `battle_id`, `date`, Stadiums.name AS `location`, winner.name AS `winner`, loser.name AS `loser`
FROM `Battles` 
INNER JOIN `Stadiums` ON Stadiums.stadium_id = Battles.stadium_id
INNER JOIN `Trainers` winner ON winner.trainer_id = Battles.winning_trainer
INNER JOIN `Trainers` loser ON loser.trainer_id = Battles.losing_trainer
ORDER BY `battle_id`;

-- get a single Battle's data for the Update Battle Form
SELECT `battle_id`, `date`, Stadiums.name AS `location`, winner.name AS `winner`, loser.name AS `loser`
FROM `Battles` 
INNER JOIN `Stadiums` ON Stadiums.stadium_id = Battles.stadium_id
INNER JOIN `Trainers` winner ON winner.trainer_id = Battles.winning_trainer
INNER JOIN `Trainers` loser ON loser.trainer_id = Battles.losing_trainer
WHERE `battle_id` = :battle_id_from_browser;

-- update a single Battle's data for the Update Battle Form
UPDATE `Battles`
SET
  `date` = :date_input,
  `stadium_id` = (SELECT `stadium_id` FROM `Stadiums` WHERE `name` = :name_input),
  `winning_trainer` = (SELECT `trainer_id` FROM `Trainers` WHERE `name` = :name_input),
  `losing_trainer` = (SELECT `trainer_id` FROM `Trainers` WHERE `name` = :name_input)
WHERE `battle_id` = :battle_id_from_browser;

-- insert a new Battle for the Add Battle Form
INSERT INTO `Battles` (
  `date`,
  `stadium_id`,
  `winning_trainer`,
  `losing_trainer`
)
VALUES (
  :date_input,
  (SELECT `stadium_id` FROM `Stadiums` WHERE `name` = :name_input),
  (SELECT `trainer_id` FROM `Trainers` WHERE `name` = :name_input),
  (SELECT `trainer_id` FROM `Trainers` WHERE `name` = :name_input)
);

-- delete a Battle in Current Battles
DELETE FROM `Battles` WHERE `battle_id` = :battle_id_from_browser;

-- -----------------------------------------
-- Pokemons_Battles queries 
-- -----------------------------------------
-- get all fields to populate Pokemon Battle Participation
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

-- get a single Pokemon Battle Participation for Update Pokemon Battle Participation Form
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
WHERE `pokebattle_id` = :pokebattle_id_from_browser;

-- update a single Pokemon Battle Participation for the Update Pokemon Battle Participation
UPDATE `Pokemons_Battles`
SET
  `battle_id` = (SELECT `battle_id` FROM `Battles` WHERE `battle_id` = :battle_id_from_browser),
  `pokemon_id` = (SELECT `pokemon_id` FROM `Pokemons` WHERE `pokemon_id` = :pokemon_id_from_browser),
  `knocked_out` = :knocked_out_input
WHERE `pokebattle_id` = :pokebattle_id_from_browser; 

-- add a new Pokemon Battle Participation
INSERT INTO `Pokemons_Battles` (
  `battle_id`,
  `pokemon_id`,
  `knocked_out`
)
VALUES (
  (SELECT `battle_id` FROM `Battles` WHERE `battle_id` = :battle_id_from_browser),
  (SELECT `pokemon_id` FROM `Pokemons` WHERE `pokemon_id` = :pokemon_id_from_browser),
  :knocked_out_input
);

-- get pre-populated Pokemon attributes for adding new Pokemon Battle Participation
SELECT `pokemon_id`, `nickname`, Species.species AS `species`, Trainers.name AS trainer, Pokemons.trainer_id AS `trainer_id`
FROM `Pokemons` 
LEFT JOIN `Trainers` ON Trainers.trainer_id = Pokemons.trainer_id
INNER JOIN `Species` ON Species.pokedex_id = Pokemons.pokedex_id
WHERE `pokemon_id` = :pokebattle_id_from_browser;

-- delete a Pokemon Battle Participation
DELETE FROM `Pokemons_Battles` WHERE `pokebattle_id` = :pokebattle_id_from_browser;

-- get all battles to populate drop down menu for a particular trainer when adding/updating Pokemon Battle Participation
SELECT `battle_id`, `date`, Stadiums.name AS `stadium`
FROM `Battles`
INNER JOIN `Stadiums` ON Stadiums.stadium_id = Battles.stadium_id
WHERE `winning_trainer` = :trainer_id_from_browser OR `losing_trainer` = trainer_id_from_browser;