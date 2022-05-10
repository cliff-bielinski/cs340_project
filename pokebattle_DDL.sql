-- -----------------------------------------
-- Project Name: PokeBattle
-- Step 3 Draft
-- Group: The 39ers
-- Members: Clifford Bielinski, Yujun Liu
-- -----------------------------------------

SET FOREIGN_KEY_CHECKS=0;
SET AUTOCOMMIT = 0;

-- -----------------------------------------
-- Species Table
-- -----------------------------------------
DROP TABLE IF EXISTS `Species`;
CREATE TABLE `Species` (
  `pokedex_id` INT(3) NOT NULL UNIQUE,
  `species` VARCHAR(12) NOT NULL,
  `type` VARCHAR(10) NOT NULL,
  `secondary_type` VARCHAR(10),
  PRIMARY KEY (`pokedex_id`)
);

-- ------------------------------------------
-- Stadiums Table
-- ------------------------------------------
DROP TABLE IF EXISTS `Stadiums`;
CREATE TABLE `Stadiums` (
  `stadium_id` INT NOT NULL UNIQUE AUTO_INCREMENT,
  `name` VARCHAR(50) NOT NULL,
  `location` VARCHAR(50) NOT NULL,
  PRIMARY KEY (`stadium_id`)
);

-- ------------------------------------------
-- Trainers Table
-- ------------------------------------------
DROP TABLE IF EXISTS `Trainers`;
CREATE TABLE `Trainers` (
  `trainer_id` INT NOT NULL UNIQUE AUTO_INCREMENT,
  `name` VARCHAR(50) NOT NULL,
  `birthdate` DATE NOT NULL,
  `gender` VARCHAR(12) NOT NULL,
  PRIMARY KEY (`trainer_id`)
);

-- ------------------------------------------
-- Pokemons Table
-- ------------------------------------------
DROP TABLE IF EXISTS `Pokemons`;
CREATE TABLE `Pokemons` (
  `pokemon_id` INT NOT NULL UNIQUE AUTO_INCREMENT,
  `nickname` VARCHAR(50),
  `gender` VARCHAR(12),
  `level` INT(3) NOT NULL,
  `pokedex_id` INT(3) NOT NULL,
  `trainer_id` INT,
  PRIMARY KEY (`pokemon_id`),
  FOREIGN KEY (`pokedex_id`) REFERENCES `Species`(`pokedex_id`) ON DELETE RESTRICT,
  FOREIGN KEY (`trainer_id`) REFERENCES `Trainers`(`trainer_id`) ON DELETE SET NULL
);

-- ------------------------------------------
-- Battles Table
-- ------------------------------------------
DROP TABLE IF EXISTS `Battles`;
CREATE TABLE `Battles` (
  `battle_id` INT NOT NULL UNIQUE AUTO_INCREMENT,
  `date` DATE NOT NULL,
  `stadium_id` INT NOT NULL,
  `winning_trainer` INT NOT NULL,
  `losing_trainer` INT NOT NULL,
  PRIMARY KEY (`battle_id`),
  FOREIGN KEY (`stadium_id`) REFERENCES `Stadiums`(`stadium_id`) ON DELETE CASCADE,
  FOREIGN KEY (`winning_trainer`) REFERENCES `Trainers`(`trainer_id`) ON DELETE RESTRICT,
  FOREIGN KEY (`losing_trainer`) REFERENCES `Trainers`(`trainer_id`) ON DELETE RESTRICT
);

-- ------------------------------------------
-- Pokemons_Battles Table
-- ------------------------------------------
DROP TABLE IF EXISTS `Pokemons_Battles`;
CREATE TABLE `Pokemons_Battles` (
  `pokebattle_id` INT NOT NULL UNIQUE AUTO_INCREMENT,
  `battle_id` INT NOT NULL,
  `pokemon_id` INT NOT NULL,
  `knocked_out` TINYINT(1) NOT NULL,
  PRIMARY KEY (`pokebattle_id`),
  FOREIGN KEY (`battle_id`) REFERENCES `Battles`(`battle_id`) ON DELETE CASCADE,
  FOREIGN KEY (`pokemon_id`) REFERENCES `Pokemons`(`pokemon_id`) ON DELETE CASCADE
);

-- ------------------------------------------
-- Populate Species Table with Sample Data
-- ------------------------------------------
INSERT INTO `Species` (
  `pokedex_id`,
  `species`,
  `type`,
  `secondary_type`
)
VALUES
  (1, 'Bulbasaur', 'Grass', 'Poison'),
  (16, 'Pidgey', 'Normal', 'Flying'),
  (25, 'Pikachu', 'Electric', NULL),
  (39, 'Jigglypuff', 'Normal', 'Fairy'),
  (150, 'Mewtwo', 'Psychic', NULL);

-- ------------------------------------------
-- Populate Stadiums Table with Sample Data
-- ------------------------------------------
INSERT INTO `Stadiums` (
  `name`,
  `location`
)
VALUES
  ('Pewter Gym', 'Pewter City'),
  ('Vermillion Gym', 'Vermillion City'),
  ('Fuschia Gym', 'Fuschia City'),
  ('Cinnabar Gym', 'Cinnabar Island'),
  ('Cerulean Gym', 'Cerulean City');

-- ------------------------------------------
-- Populate Trainers Table with Sample Data
-- ------------------------------------------
INSERT INTO `Trainers` (
  `name`,
  `birthdate`,
  `gender`
)
VALUES
  ('Ash Ketchum', '1996-12-01', 'Male'),
  ('Misty Williams', '1994-02-14', 'Female'),
  ('Gary Oak', '1996-04-12', 'Male'),
  ('Brock Harrison', '1992-06-17', 'Male'),
  ('James Kojiro', '1988-07-05', 'Male');

-- ------------------------------------------
-- Populate Pokemons Table with Sample Data
-- ------------------------------------------
INSERT INTO `Pokemons` (
  `nickname`,
  `gender`,
  `level`,
  `pokedex_id`,
  `trainer_id`
)
VALUES
  (
    'Zaps',
    'Male',
    15,
    (SELECT `pokedex_id` FROM `Species` WHERE `pokedex_id` = 25),
    (SELECT `trainer_id` FROM `Trainers` WHERE `trainer_id` = 1)
  ),
  (
    NULL,
    'Female',
    17,
    (SELECT `pokedex_id` FROM `Species` WHERE `pokedex_id` = 25),
    (SELECT `trainer_id` FROM `Trainers` WHERE `trainer_id` = 3)
  ),
  (
    'Bulba',
    'Female',
    5,
    (SELECT `pokedex_id` FROM `Species` WHERE `pokedex_id` = 1),
    (SELECT `trainer_id` FROM `Trainers` WHERE `trainer_id` = 2)
  ),
  (
    'Beaks',
    NULL,
    22,
    (SELECT `pokedex_id` FROM `Species` WHERE `pokedex_id` = 16),
    (SELECT `trainer_id` FROM `Trainers` WHERE `trainer_id` = 4) 
  ),
  (
    NULL,
    'Male',
    30,
    (SELECT `pokedex_id` FROM `Species` WHERE `pokedex_id` = 39),
    NULL
  ),
  (
    NULL,
    NULL,
    100,
    (SELECT `pokedex_id` FROM `Species` WHERE `pokedex_id` = 150),
    (SELECT `trainer_id` FROM `Trainers` WHERE `trainer_id` = 1) 
  );

-- ------------------------------------------
-- Populate Battles Table with Sample Data
-- ------------------------------------------
INSERT INTO `Battles` (
  `date`,
  `stadium_id`,
  `winning_trainer`,
  `losing_trainer`
)
VALUES
  (
    '2022-02-01',
    (SELECT `stadium_id` FROM `Stadiums` WHERE `stadium_id` = 5),
    (SELECT `trainer_id` FROM `Trainers` WHERE `trainer_id` = 1),
    (SELECT `trainer_id` FROM `Trainers` WHERE `trainer_id` = 2)
  ),
  (
    '2022-03-16',
    (SELECT `stadium_id` FROM `Stadiums` WHERE `stadium_id` = 1),
    (SELECT `trainer_id` FROM `Trainers` WHERE `trainer_id` = 1),
    (SELECT `trainer_id` FROM `Trainers` WHERE `trainer_id` = 4)
  ),
  (
    '2022-03-16',
    (SELECT `stadium_id` FROM `Stadiums` WHERE `stadium_id` = 4),
    (SELECT `trainer_id` FROM `Trainers` WHERE `trainer_id` = 3),
    (SELECT `trainer_id` FROM `Trainers` WHERE `trainer_id` = 5)
  ),
  (
    '2022-03-26',
    (SELECT `stadium_id` FROM `Stadiums` WHERE `stadium_id` = 1),
    (SELECT `trainer_id` FROM `Trainers` WHERE `trainer_id` = 3),
    (SELECT `trainer_id` FROM `Trainers` WHERE `trainer_id` = 4)
  ),
  (
    '2022-04-03',
    (SELECT `stadium_id` FROM `Stadiums` WHERE `stadium_id` = 2),
    (SELECT `trainer_id` FROM `Trainers` WHERE `trainer_id` = 5),
    (SELECT `trainer_id` FROM `Trainers` WHERE `trainer_id` = 3)
  );

-- -------------------------------------------------
-- Populate Pokemons_Battles Table with Sample Data
-- -------------------------------------------------
INSERT INTO `Pokemons_Battles` (
  `battle_id`,
  `pokemon_id`,
  `knocked_out`
)
VALUES
  (
    (SELECT `battle_id` FROM `Battles` WHERE `battle_id` = 1),
    (SELECT `pokemon_id` FROM `Pokemons` WHERE `pokemon_id` = 1),
    0
  ),
  (
    (SELECT `battle_id` FROM `Battles` WHERE `battle_id` = 2),
    (SELECT `pokemon_id` FROM `Pokemons` WHERE `pokemon_id` = 1),
    0
  ),
  (
    (SELECT `battle_id` FROM `Battles` WHERE `battle_id` = 1),
    (SELECT `pokemon_id` FROM `Pokemons` WHERE `pokemon_id` = 3),
    1
  ),
  (
    (SELECT `battle_id` FROM `Battles` WHERE `battle_id` = 3),
    (SELECT `pokemon_id` FROM `Pokemons` WHERE `pokemon_id` = 2),
    0
  ),
  (
    (SELECT `battle_id` FROM `Battles` WHERE `battle_id` = 2),
    (SELECT `pokemon_id` FROM `Pokemons` WHERE `pokemon_id` = 4),
    1
  );

SET FOREIGN_KEY_CHECKS=1;
COMMIT;
